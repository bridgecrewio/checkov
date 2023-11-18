from datetime import datetime, timezone

from time_machine import travel

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.report import Report
from checkov.common.output.spdx import SPDX
from checkov.common.sca.output import create_report_cve_record


@travel(datetime(2022, 12, 24, tzinfo=timezone.utc))
def test_sca_package_output():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    vulnerability_details = {
        "id": "CVE-2019-19844",
        "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
        "cvss": 9.8,
        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ...",
        "severity": "moderate",
        "packageName": "django",
        "packageVersion": "1.2",
        "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
        "riskFactors": ["Attack complexity: low", "Attack vector: network", "Critical severity", "Has fix"],
        "impactedVersions": ["<1.11.27"],
        "publishedDate": "2019-12-18T20:15:00+01:00",
        "discoveredDate": "2019-12-18T19:15:00Z",
        "fixDate": "2019-12-18T20:15:00+01:00",
    }

    record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses="OSI_BDS",
        package={"package_registry": "https://registry.npmjs.org/", "is_private_registry": False},
    )
    # also add a BC_VUL_2 record
    bc_record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses="OSI_BDS",
        package={"package_registry": "https://registry.npmjs.org/", "is_private_registry": False},
    )
    bc_record.check_id = "BC_VUL_2"

    report = Report(CheckType.SCA_PACKAGE)
    report.add_resource(record.resource)
    report.add_record(record)
    report.add_record(bc_record)

    report.extra_resources.add(
        ExtraResource(
            file_abs_path=file_abs_path,
            file_path=f"/{rootless_file_path}",
            resource=f"{rootless_file_path}.testpkg",
            vulnerability_details={"package_name": "testpkg", "package_version": "1.1.1", "licenses": "MIT"},
        )
    )

    # when
    spdx = SPDX(repo_id="example", reports=[report])

    # override dynamic data
    spdx.document.creation_info.document_namespace = "https://spdx.org/spdxdocs/checkov-sbom-9.9.9"

    # then
    output = spdx.get_tag_value_output()

    # remove dynamic data
    assert output == "".join(
        [
            "## Document Information\n",
            "SPDXVersion: SPDX-2.3\n",
            "DataLicense: CC0-1.0\n",
            "SPDXID: SPDXRef-DOCUMENT\n",
            "DocumentName: checkov-sbom\n",
            "DocumentNamespace: https://spdx.org/spdxdocs/checkov-sbom-9.9.9\n",
            "\n",
            "## Creation Information\n",
            "Creator: Tool: checkov\n",
            "Creator: Organization: bridgecrew (meet@bridgecrew.io)\n",
            "Created: 2022-12-24T00:00:00Z\n",
            "\n",
            "## Package Information\n",
            "PackageName: django\n",
            "SPDXID: SPDXRef-django\n",
            "PackageVersion: 1.2\n",
            "PackageFileName: /requirements.txt\n",
            "PackageDownloadLocation: NONE\n",
            "FilesAnalyzed: true\n",
            "PackageLicenseInfoFromFiles: OSI_BDS\n",
            "\n",
            "## Package Information\n",
            "PackageName: testpkg\n",
            "SPDXID: SPDXRef-testpkg\n",
            "PackageVersion: 1.1.1\n",
            "PackageFileName: /requirements.txt\n",
            "PackageDownloadLocation: NONE\n",
            "FilesAnalyzed: true\n",
            "PackageLicenseInfoFromFiles: MIT\n",
            "\n",
            "\n",
        ]
    )
