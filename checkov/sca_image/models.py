from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class ReportCVE:
    cveId: str
    status: str
    severity: str
    packageName: str
    packageVersion: str
    link: str | None
    publishedDate: str
    cvss: int | None
    vector: str | None
    description: str | None
    riskFactors: Any | None
