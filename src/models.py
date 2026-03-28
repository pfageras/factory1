from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AffectedPackage:
    ecosystem: str
    name: str
    vulnerable_range: str
    patched_version: str | None


@dataclass
class CVE:
    id: str
    description: str
    cvss_score: float | None
    severity: str
    last_modified: datetime
    source: str = "nvd"
    packages: list[AffectedPackage] = field(default_factory=list)
    advisory_type: str = "reviewed"  # "reviewed" or "malware"
