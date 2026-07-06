"""
Regression tests for the github_failed_only formatter — SCA package scan output.

Covers the fix for PCSUP-31519:
  print_failed_github_md() was using a static IaC-only table for all check types,
  silently dropping all CVE-specific data (CVE ID, package name, version, severity,
  fix version) from sca_package and sca_image reports.

Fix location: checkov/common/output/report.py — print_failed_github_md()
"""
from __future__ import annotations

import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record, SCA_PACKAGE_SCAN_CHECK_NAME
from checkov.common.output.report import Report


def _make_sca_record(
    cve_id: str = "CVE-2019-19844",
    package_name: str = "django",
    package_version: str = "1.2",
    severity: str = "critical",
    lowest_fixed_version: str = "3.0.1",
    file_path: str = "/requirements.txt",
) -> Record:
    """
    Build a minimal SCA failed Record that mirrors what the sca_package_2 runner
    produces. No API key or runner invocation required.
    """
    return Record(
        check_id=f"BC_{cve_id.replace('-', '_')}",
        check_name=SCA_PACKAGE_SCAN_CHECK_NAME,
        check_result={"result": CheckResult.FAILED},
        code_block=None,
        file_path=file_path,
        file_line_range=[0, 0],
        resource=f"python-{package_name}-{package_version}",
        evaluations=None,
        check_class="",
        file_abs_path=file_path,
        vulnerability_details={
            "id": cve_id,
            "package_name": package_name,
            "package_version": package_version,
            "severity": severity,
            "fix_version": lowest_fixed_version,
            "lowest_fixed_version": lowest_fixed_version,
            "status": f"fixed in {lowest_fixed_version}",
            "cvss": 9.8,
            "description": "Test CVE description.",
        },
    )


class TestPrintFailedGithubMdSca:
    """Tests for print_failed_github_md() with sca_package check type."""

    def test_cve_id_present_in_output(self) -> None:
        """CVE ID must appear in the github_failed_only Markdown output."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record())

        output = report.print_failed_github_md()

        assert "CVE-2019-19844" in output, (
            f"CVE ID missing from output.\nActual output:\n{output}"
        )

    def test_package_name_present_in_output(self) -> None:
        """Package name must appear in the github_failed_only Markdown output."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record())

        output = report.print_failed_github_md()

        assert "django" in output, (
            f"Package name missing from output.\nActual output:\n{output}"
        )

    def test_package_version_present_in_output(self) -> None:
        """Affected package version must appear in the output."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record())

        output = report.print_failed_github_md()

        assert "1.2" in output, (
            f"Package version missing from output.\nActual output:\n{output}"
        )

    def test_severity_present_in_output(self) -> None:
        """Severity must appear in the github_failed_only Markdown output."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record())

        output = report.print_failed_github_md()

        assert "critical" in output, (
            f"Severity missing from output.\nActual output:\n{output}"
        )

    def test_fixed_version_present_in_output(self) -> None:
        """Fixed version must appear in the github_failed_only Markdown output."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record())

        output = report.print_failed_github_md()

        assert "3.0.1" in output, (
            f"Fixed version missing from output.\nActual output:\n{output}"
        )

    def test_sca_headers_used_not_iac_headers(self) -> None:
        """Output must use SCA-specific column headers, not IaC headers."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record())

        output = report.print_failed_github_md()

        # SCA headers must be present
        assert "CVE ID" in output, f"'CVE ID' header missing.\nActual output:\n{output}"
        assert "Package" in output, f"'Package' header missing.\nActual output:\n{output}"
        assert "Severity" in output, f"'Severity' header missing.\nActual output:\n{output}"
        assert "Fixed Version" in output, f"'Fixed Version' header missing.\nActual output:\n{output}"

        # IaC-only headers must NOT be present
        assert "Check Name" not in output, (
            f"IaC 'Check Name' header should not appear in SCA output.\nActual output:\n{output}"
        )
        assert "Guideline" not in output, (
            f"IaC 'Guideline' header should not appear in SCA output.\nActual output:\n{output}"
        )

    def test_multiple_cves_each_row_distinct(self) -> None:
        """Multiple CVEs for the same package must produce distinct rows."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(
            _make_sca_record(cve_id="CVE-2020-8908", severity="low", lowest_fixed_version="32.0.0")
        )
        report.failed_checks.append(
            _make_sca_record(cve_id="CVE-2023-2976", severity="high", lowest_fixed_version="32.0.0")
        )

        output = report.print_failed_github_md()

        assert "CVE-2020-8908" in output, f"First CVE missing.\nActual output:\n{output}"
        assert "CVE-2023-2976" in output, f"Second CVE missing.\nActual output:\n{output}"
        assert "low" in output, f"'low' severity missing.\nActual output:\n{output}"
        assert "high" in output, f"'high' severity missing.\nActual output:\n{output}"

    def test_summary_line_present(self) -> None:
        """The passed/failed/skipped summary line must still appear."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record())

        output = report.print_failed_github_md()

        assert "Failed Checks: 1" in output, (
            f"Summary line missing.\nActual output:\n{output}"
        )

    def test_empty_report_returns_separator(self) -> None:
        """An SCA report with no failed checks must return the separator string."""
        report = Report(check_type=CheckType.SCA_PACKAGE)

        output = report.print_failed_github_md()

        assert output.strip() == "---", (
            f"Empty report should return separator.\nActual output:\n{output}"
        )

    def test_file_path_present_in_output(self) -> None:
        """The file path must appear in the output."""
        report = Report(check_type=CheckType.SCA_PACKAGE)
        report.failed_checks.append(_make_sca_record(file_path="/app/requirements.txt"))

        output = report.print_failed_github_md()

        assert "/app/requirements.txt" in output, (
            f"File path missing from output.\nActual output:\n{output}"
        )


class TestPrintFailedGithubMdIac:
    """Regression tests: IaC path must be unaffected by the SCA fix."""

    def _make_iac_record(self) -> Record:
        return Record(
            check_id="CKV_AWS_1",
            check_name="Ensure S3 bucket has versioning enabled",
            check_result={"result": CheckResult.FAILED},
            code_block=None,
            file_path="/main.tf",
            file_line_range=[1, 10],
            resource="aws_s3_bucket.example",
            evaluations=None,
            check_class="",
            file_abs_path="/main.tf",
        )

    def test_iac_check_id_present(self) -> None:
        """IaC check ID must appear in the output."""
        report = Report(check_type=CheckType.TERRAFORM)
        report.failed_checks.append(self._make_iac_record())

        output = report.print_failed_github_md()

        assert "CKV_AWS_1" in output, f"IaC check ID missing.\nActual output:\n{output}"

    def test_iac_resource_present(self) -> None:
        """IaC resource must appear in the output."""
        report = Report(check_type=CheckType.TERRAFORM)
        report.failed_checks.append(self._make_iac_record())

        output = report.print_failed_github_md()

        assert "aws_s3_bucket.example" in output, (
            f"IaC resource missing.\nActual output:\n{output}"
        )

    def test_iac_uses_iac_headers(self) -> None:
        """IaC output must use the original IaC column headers."""
        report = Report(check_type=CheckType.TERRAFORM)
        report.failed_checks.append(self._make_iac_record())

        output = report.print_failed_github_md()

        assert "Check ID" in output, f"'Check ID' header missing.\nActual output:\n{output}"
        assert "Check Name" in output, f"'Check Name' header missing.\nActual output:\n{output}"
        assert "Resource" in output, f"'Resource' header missing.\nActual output:\n{output}"
        assert "Guideline" in output, f"'Guideline' header missing.\nActual output:\n{output}"

        # SCA-specific headers must NOT appear in IaC output
        assert "CVE ID" not in output, (
            f"SCA 'CVE ID' header should not appear in IaC output.\nActual output:\n{output}"
        )
