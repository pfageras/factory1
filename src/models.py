from dataclasses import dataclass
from datetime import datetime


@dataclass
class CVE:
    id: str
    description: str
    cvss_score: float | None
    severity: str
    last_modified: datetime
