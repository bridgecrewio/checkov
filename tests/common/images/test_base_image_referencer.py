import unittest
from pathlib import PureWindowsPath
from unittest import mock


class TestImageReferencerBase(unittest.TestCase):
    # noinspection PyMethodMayBeStatic
    def run_is_valid_public_image_valid(self, image_name: str) -> bool:
        from checkov.common.images.image_referencer import is_valid_public_image_name
        return is_valid_public_image_name(image_name)

    def test_invalid_image_name_replace(self):
        self.assertFalse(self.run_is_valid_public_image_valid('registry-auth.twistlock.com/tw_<REPLACE_TWISTLOCK_TOKEN>/twistlock/console:console_20_04_163'))

    def test_invalid_image_name_extraction(self):
        self.assertFalse(self.run_is_valid_public_image_valid(
            "gcr.io/[\"${{'develop': {'project_id': 'develop'}, 'production': {'project_id': 'production'}}[\"var.env\"].project_id}\"]/notifier:aa123aa"
        ))

    def test_invalid_image_name_var_reference(self):
        self.assertFalse(self.run_is_valid_public_image_valid('gcr.io/example/base:$IMAGE_TAG'))

    def test_localhost_image_name(self):
        self.assertFalse(self.run_is_valid_public_image_valid('localhost:320000/video-conferencing-ms-example'))

    def test_cname_with_port_image_name(self):
        self.assertFalse(self.run_is_valid_public_image_valid('example.local:5004/video-conferencing-ms-example:1.2.3'))

    def test_valid_image_name(self):
        self.assertTrue(self.run_is_valid_public_image_valid('node:16'))

    def test_valid_image_name_2(self):
        self.assertTrue(self.run_is_valid_public_image_valid('ubuntu'))

    def test_valid_image_name_3(self):
        self.assertTrue(self.run_is_valid_public_image_valid('gcr.io/develop/notifier:aa123aa'))

    def test_add_image_records_preserves_windows_path_separator(self):
        """A Windows-style dockerfile path must keep its separators in the record file_path.

        The previous `path.replace(Path(path).anchor, "", 1)` resolved `anchor` to a bare
        backslash and removed the first backslash anywhere in the string, dropping the
        separator between path segments.

        Patching `IS_WINDOWS` and `Path` reproduces the Windows condition on any host.
        """
        from checkov.common.bridgecrew.check_type import CheckType
        from checkov.common.images.image_referencer import Image, ImageReferencerMixin
        from checkov.common.output.report import Report
        from checkov.runner_filter import RunnerFilter

        dockerfile_path = "/my-project.api\\client\\Dockerfile.base"
        cached_results = {
            "results": [
                {
                    "id": "sha256:" + "1" * 64,
                    "name": "node:24.15.0",
                    "distro": "Debian GNU/Linux 12 (bookworm)",
                    "distroRelease": "bookworm",
                    "packages": [{"type": "os", "name": "openssl", "version": "3.0.11-1"}],
                    "vulnerabilities": [
                        {
                            "id": "CVE-2023-5678",
                            "status": "fixed in 3.0.12",
                            "cvss": 5.3,
                            "description": "test vulnerability",
                            "severity": "medium",
                            "packageName": "openssl",
                            "packageVersion": "3.0.11-1",
                            "link": "https://nvd.nist.gov/vuln/detail/CVE-2023-5678",
                            "riskFactors": ["Medium severity", "Has fix"],
                            "impactedVersions": ["<3.0.12"],
                            "publishedDate": "2023-11-06T00:00:00Z",
                            "discoveredDate": "2023-11-06T00:00:00Z",
                            "fixDate": "2023-11-06T00:00:00Z",
                        }
                    ],
                }
            ]
        }

        class _Referencer(ImageReferencerMixin[None]):
            def extract_images(self, graph_connector=None, definitions=None, definitions_raw=None):
                return []

        report = Report(CheckType.SCA_IMAGE)
        image = Image(file_path=dockerfile_path, name="node:24.15.0", start_line=1, end_line=1)

        with mock.patch("checkov.common.images.image_referencer.IS_WINDOWS", True), \
                mock.patch("checkov.common.images.image_referencer.Path", PureWindowsPath), \
                mock.patch(
                    "checkov.common.images.image_referencer."
                    "docker_image_scanning_integration.create_report",
                    return_value={},
                ):
            _Referencer()._add_image_records(
                report=report,
                root_path=None,
                check_class="checkov.common.bridgecrew.vulnerability_scanning.image_scanner.ImageScanner",
                dockerfile_path=dockerfile_path,
                image=image,
                runner_filter=RunnerFilter(),
                report_type=CheckType.SCA_IMAGE,
                bc_integration=mock.MagicMock(),
                cached_results=cached_results,
                license_statuses=[],
                file_line_range=[1, 1],
            )

        records = report.failed_checks + report.passed_checks
        self.assertTrue(records, "expected at least one vulnerability record")
        for record in records:
            # the separator between 'my-project.api' and 'client' must survive
            self.assertNotIn("my-project.apiclient", record.file_path)
            self.assertTrue(record.file_path.startswith("/my-project.api\\client\\Dockerfile.base "))
