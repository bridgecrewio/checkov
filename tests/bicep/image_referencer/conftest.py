from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture()
def image_cached_result() -> dict[str, Any]:
    return {
        "results": [
            {
                "id": "sha256:f9b91f78b0344fa0efc5583d79e78a90556ab0bb3f93fcbc8728b0b70d29a5db",
                "name": "python:3.9-alpine",
                "distro": "Alpine Linux v3.16",
                "distroRelease": "3.16.1",
                "digest": "sha256:83a343afa488ff14d0c807b62770140d2ec30ef2e83a3a45c4ce62c29623e240",
                "collections": ["All"],
                "packages": [{"type": "os", "name": "zlib", "version": "1.2.12-r1", "licenses": ["Zlib"]}],
                "compliances": [],
                "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
                "complianceScanPassed": True,
                "vulnerabilities": [
                    {
                        "id": "CVE-2022-37434",
                        "status": "fixed in 1.2.12-r2",
                        "description": "zlib through 1.2.12 has a heap-based buffer over-read ...",
                        "severity": "low",
                        "packageName": "zlib",
                        "packageVersion": "1.2.12-r1",
                        "link": "https://nvd.nist.gov/vuln/detail/CVE-2022-37434",
                        "riskFactors": ["Has fix", "Recent vulnerability"],
                        "impactedVersions": ["<1.2.12-r2"],
                        "publishedDate": "2022-08-05T07:15:00Z",
                        "discoveredDate": "2022-08-08T13:45:43Z",
                        "fixDate": "2022-08-05T07:15:00Z",
                    }
                ],
                "vulnerabilityDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 1, "total": 1},
                "vulnerabilityScanPassed": True,
            }
        ]
    }


@pytest.fixture()
def license_statuses_result() -> list[dict[str, str]]:
    return [
        {
            "package_name": "openssl",
            "package_version": "1.1.1q-r0",
            "policy": "BC_LIC_1",
            "license": "OpenSSL",
            "status": "OPEN",
        },
        {
            "package_name": "musl",
            "package_version": "1.2.3-r0",
            "policy": "BC_LIC_1",
            "license": "MIT",
            "status": "COMPLIANT",
        },
    ]
