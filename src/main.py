import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.models import CVE
from src.nvd_client import fetch_cves

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 2 * 60 * 60  # 2 hours

# In-memory cache
_cached_cves: list[CVE] = []
_last_updated: datetime | None = None


async def _poll_nvd():
    global _cached_cves, _last_updated
    while True:
        try:
            logger.info("Polling NVD API...")
            cves = await fetch_cves(days=7)
            _cached_cves = cves
            _last_updated = datetime.now(timezone.utc)
            logger.info("Cache updated: %d CVEs", len(cves))
        except Exception:
            logger.exception("Failed to fetch CVEs from NVD — keeping cached data")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_poll_nvd())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="VulnSite", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/cves")
async def get_cves():
    return {
        "cves": [
            {
                "id": cve.id,
                "description": cve.description,
                "cvss_score": cve.cvss_score,
                "severity": cve.severity,
                "last_modified": cve.last_modified.isoformat(),
            }
            for cve in _cached_cves
        ],
        "last_updated": _last_updated.isoformat() if _last_updated else None,
        "total": len(_cached_cves),
    }


# Static files mounted last — catches all unmatched routes
static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
