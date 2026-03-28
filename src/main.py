import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

from src.models import CVE
from src.nvd_client import fetch_cves
from src.github_client import fetch_github_advisories

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 2 * 60 * 60  # 2 hours

# In-memory cache
_cached_cves: list[CVE] = []
_last_updated: datetime | None = None


def _merge_data(nvd_cves: list[CVE], github_advisories: list[CVE]) -> list[CVE]:
    """Merge NVD and GitHub data. Enrich NVD entries with package info where CVE-ID matches."""
    nvd_by_id: dict[str, CVE] = {c.id: c for c in nvd_cves}
    merged: list[CVE] = list(nvd_cves)

    for adv in github_advisories:
        if adv.id in nvd_by_id:
            # Enrich existing NVD entry with package info
            existing = nvd_by_id[adv.id]
            existing.packages = adv.packages
            existing.source = "both"
            existing.advisory_type = adv.advisory_type
        else:
            # GitHub-only advisory (no matching CVE in NVD)
            merged.append(adv)

    merged.sort(key=lambda c: c.last_modified, reverse=True)
    return merged


# Separate caches per source — preserved across poll failures
_last_nvd: list[CVE] = []
_last_github: list[CVE] = []


async def _poll_sources():
    global _cached_cves, _last_updated, _last_nvd, _last_github
    while True:
        try:
            logger.info("Polling NVD API...")
            _last_nvd = await fetch_cves(days=7)
            logger.info("NVD: %d CVEs", len(_last_nvd))
        except Exception:
            logger.exception("Failed to fetch CVEs from NVD — keeping previous NVD data")

        try:
            logger.info("Polling GitHub Advisory API...")
            _last_github = await fetch_github_advisories(days=7)
            logger.info("GitHub: %d advisories", len(_last_github))
        except Exception:
            logger.exception("Failed to fetch GitHub advisories — keeping previous GitHub data")

        if _last_nvd or _last_github:
            _cached_cves = _merge_data(list(_last_nvd), _last_github)
            _last_updated = datetime.now(timezone.utc)
            logger.info("Cache updated: %d total entries", len(_cached_cves))
        else:
            logger.warning("No data from any source — keeping cached data")

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_poll_sources())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="VulnSite", version="0.2.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


def _serialize_cve(cve: CVE) -> dict:
    return {
        "id": cve.id,
        "description": cve.description,
        "cvss_score": cve.cvss_score,
        "severity": cve.severity,
        "last_modified": cve.last_modified.isoformat(),
        "source": cve.source,
        "advisory_type": cve.advisory_type,
        "packages": [
            {
                "ecosystem": p.ecosystem,
                "name": p.name,
                "vulnerable_range": p.vulnerable_range,
                "patched_version": p.patched_version,
            }
            for p in cve.packages
        ],
    }


@app.get("/api/cves")
async def get_cves(filter: str = Query("all", pattern="^(all|supply_chain|malware)$")):
    if filter == "supply_chain":
        filtered = [c for c in _cached_cves if c.packages]
    elif filter == "malware":
        filtered = [c for c in _cached_cves if c.advisory_type == "malware"]
    else:
        filtered = _cached_cves

    return {
        "cves": [_serialize_cve(c) for c in filtered],
        "last_updated": _last_updated.isoformat() if _last_updated else None,
        "total": len(filtered),
        "filter": filter,
    }


# Static files mounted last — catches all unmatched routes
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
