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

@dataclass
class ImageCachedResult:
    dockerImageName: str
    dockerFilePath: str
    dockerFileContent: str
    type: str
    sourceId: str | None
    branch: str | None
    sourceType: str
    vulnerabilities: list[ReportCVE]
    packages: list[dict[str, Any]]
    relatedResourceId: str
    cicdDetails: dict[str, Any] | None
    errorLines: list[int] | None


