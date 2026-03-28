import logging
import os
from datetime import datetime, timezone, timedelta

import httpx

from src.models import CVE, AffectedPackage

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/advisories"
PER_PAGE = 100


def _parse_advisory(adv: dict) -> CVE | None:
    ghsa_id = adv.get("ghsa_id", "")
    cve_id = adv.get("cve_id")
    advisory_id = cve_id or ghsa_id
    if not advisory_id:
        return None

    summary = adv.get("summary", "")
    description = adv.get("description", "")
    display_text = summary or description
    if len(display_text) > 500:
        display_text = display_text[:500]

    severity = (adv.get("severity") or "unknown").upper()

    cvss_score = None
    cvss_severities = adv.get("cvss_severities") or {}
    for key in ("cvss_v4", "cvss_v3"):
        cvss_data = cvss_severities.get(key)
        if cvss_data and cvss_data.get("score"):
            cvss_score = cvss_data["score"]
            break

    updated_str = adv.get("updated_at") or adv.get("published_at", "")
    try:
        last_modified = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        last_modified = datetime.now(timezone.utc)

    packages = []
    for vuln in adv.get("vulnerabilities") or []:
        pkg = vuln.get("package") or {}
        ecosystem = pkg.get("ecosystem", "")
        name = pkg.get("name", "")
        if ecosystem and name:
            packages.append(AffectedPackage(
                ecosystem=ecosystem,
                name=name,
                vulnerable_range=vuln.get("vulnerable_version_range") or "",
                patched_version=vuln.get("first_patched_version"),
            ))

    advisory_type = adv.get("type", "reviewed")

    return CVE(
        id=advisory_id,
        description=display_text,
        cvss_score=cvss_score,
        severity=severity,
        last_modified=last_modified,
        source="github",
        packages=packages,
        advisory_type=advisory_type,
    )


async def _fetch_advisories_by_type(
    client: httpx.AsyncClient,
    headers: dict,
    advisory_type: str,
    since: str,
) -> list[CVE]:
    advisories: list[CVE] = []
    url: str | None = GITHUB_API_URL
    params = {
        "type": advisory_type,
        "sort": "updated",
        "direction": "desc",
        "per_page": PER_PAGE,
        "updated": f">{since}",
    }

    while url:
        logger.info("Fetching GitHub advisories type=%s (count so far: %d)", advisory_type, len(advisories))
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()

        for adv in response.json():
            cve = _parse_advisory(adv)
            if cve:
                advisories.append(cve)

        # Cursor-based pagination via Link header
        url = None
        params = {}  # Next URL includes all params
        link_header = response.headers.get("link", "")
        for part in link_header.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
                break

    return advisories


async def fetch_github_advisories(days: int = 7) -> list[CVE]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_advisories: list[CVE] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for advisory_type in ("reviewed", "malware"):
            try:
                result = await _fetch_advisories_by_type(client, headers, advisory_type, since)
                all_advisories.extend(result)
            except Exception:
                logger.exception("Failed to fetch GitHub advisories type=%s", advisory_type)

    all_advisories.sort(key=lambda c: c.last_modified, reverse=True)
    logger.info("Fetched %d GitHub advisories total", len(all_advisories))
    return all_advisories
