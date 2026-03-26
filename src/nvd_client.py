import logging
import os
from datetime import datetime, timezone, timedelta

import httpx

from src.models import CVE

logger = logging.getLogger(__name__)

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
RESULTS_PER_PAGE = 2000


def _parse_cve(vuln: dict) -> CVE | None:
    cve = vuln.get("cve", {})
    cve_id = cve.get("id", "")
    if not cve_id:
        return None

    descriptions = cve.get("descriptions", [])
    description = ""
    for desc in descriptions:
        if desc.get("lang") == "en":
            description = desc.get("value", "")
            break
    if not description and descriptions:
        description = descriptions[0].get("value", "")

    cvss_score = None
    severity = "UNKNOWN"
    metrics = cve.get("metrics", {})
    for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        metric_list = metrics.get(metric_key, [])
        if metric_list:
            cvss_data = metric_list[0].get("cvssData", {})
            cvss_score = cvss_data.get("baseScore")
            severity = cvss_data.get("baseSeverity", "UNKNOWN")
            break

    last_modified_str = cve.get("lastModified", "")
    try:
        last_modified = datetime.fromisoformat(last_modified_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        last_modified = datetime.now(timezone.utc)

    return CVE(
        id=cve_id,
        description=description,
        cvss_score=cvss_score,
        severity=severity.upper(),
        last_modified=last_modified,
    )


async def fetch_cves(days: int = 7) -> list[CVE]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    params = {
        "lastModStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000+00:00"),
        "lastModEndDate": now.strftime("%Y-%m-%dT%H:%M:%S.000+00:00"),
        "resultsPerPage": RESULTS_PER_PAGE,
        "startIndex": 0,
    }

    headers = {}
    api_key = os.environ.get("NVD_API_KEY")
    if api_key:
        headers["apiKey"] = api_key

    all_cves: list[CVE] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            logger.info("Fetching NVD CVEs (startIndex=%d)", params["startIndex"])
            response = await client.get(NVD_API_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            total_results = data.get("totalResults", 0)
            vulnerabilities = data.get("vulnerabilities", [])

            for vuln in vulnerabilities:
                cve = _parse_cve(vuln)
                if cve:
                    all_cves.append(cve)

            fetched_so_far = params["startIndex"] + len(vulnerabilities)
            if fetched_so_far >= total_results:
                break
            params["startIndex"] = fetched_so_far

    all_cves.sort(key=lambda c: c.last_modified, reverse=True)
    logger.info("Fetched %d CVEs from NVD (total_results=%d)", len(all_cves), total_results)
    return all_cves
