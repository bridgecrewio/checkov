import os
import io
from pathlib import Path
from unittest.mock import patch
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.common.output.csv import CSVSBOM
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.output.common import ImageDetails
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner


class TestBomOutput:
    def test_iac_csv_output(self, tmp_path: Path):
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/../runner_registry/example_s3_tf"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)

        with patch('sys.stdout', new=io.StringIO()) as captured_output:
            runner_registry.print_iac_bom_reports(output_path=str(tmp_path), scan_reports=reports, output_types=['csv'])
        output = captured_output.getvalue()
        assert 'Persisting SBOM to' in output
        iac_file_path = tmp_path / 'results_iac.csv'
        with open(iac_file_path) as file:
            content = file.readlines()
            header = content[:1][0]
            assert 'Resource,Path,Git Org,Git Repository,Misconfigurations,Severity\n' == header
            rows = content[1:]
            assert 'aws_s3_bucket' in rows[0]

    def test_sca_package_csv_output(self, tmp_path: Path):
        # given
        file_name = "oss_packages.csv"
        csv_sbom_report = CSVSBOM()
        report = Report(CheckType.SCA_PACKAGE)

        cve_id = "CVE-2019-1010083"
        rootless_file_path = "requirements.txt"
        file_abs_path = f"example/{rootless_file_path}"

        details = {
            "id": cve_id,
            "severity": "high",
            "package_name": "flask",
            "package_version": "0.6",
            "licenses": "",
        }
        record = Record(
            check_id=f"CKV_{cve_id.replace('-', '_')}",
            bc_check_id=f"BC_{cve_id.replace('-', '_')}",
            check_name="SCA package scan",
            check_result={"result": CheckResult.FAILED},
            code_block=[(0,"")],
            file_path=f"/{rootless_file_path}",
            file_line_range=[0, 0],
            resource="requirements.txt.flask",
            check_class="",
            evaluations=None,
            file_abs_path=file_abs_path,
            severity=Severities.get(BcSeverities.HIGH),
            vulnerability_details=details,
        )
        extra_resource = ExtraResource(
            file_abs_path=file_abs_path,
            file_path=f"/{rootless_file_path}",
            resource=f"{rootless_file_path}.requests",
            vulnerability_details={
                "package_name": "requests",
                "package_version": "",
                'licenses': 'Apache-2.0'
            }
        )

        report.add_record(record)
        report.extra_resources.add(extra_resource)
        csv_sbom_report.add_report(report=report, git_org="acme", git_repository="bridgecrewio/example")

        # when
        csv_sbom_report.persist_report_oss_packages(file_name=file_name, is_api_key=True, output_path=str(tmp_path))

        # then
        output_file_path = tmp_path / file_name
        csv_output = output_file_path.read_text()
        csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_PACKAGE)
        expected_csv = (
            "Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses\n"
            "flask,0.6,/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,\n"
            "requests,,/requirements.txt,acme,bridgecrewio/example,,,Apache-2.0\n"
        )

        assert csv_output == expected_csv

        expected_csv = (
            "Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses\n"
            "\"flask\",0.6,/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,\"\"\n"
            "\"requests\",,/requirements.txt,acme,bridgecrewio/example,,,\"Apache-2.0\"\n"
        )

        assert csv_output_str == expected_csv

    def test_sca_image_csv_output(self, tmp_path: Path):
        # given
        file_name = "container_images.csv"
        csv_sbom_report = CSVSBOM()
        report = Report(CheckType.SCA_IMAGE)

        cve_id = "CVE-2022-32207"
        rootless_file_path = "Dockerfile (sha256:ba9a86c8195c9eba8504720144d22e39736d61dcaf119e328948b4b96f118b29)"
        file_abs_path = f"example/{rootless_file_path}"

        details = {
            'id': 'CVE-2022-32091',
            'status': 'open',
            'severity': 'critical',
            'package_name': 'mariadb-10.5',
            'package_version': '1:10.5.15-0+deb11u1',
            'package_type': 'os',
            'image_details': ImageDetails(
                distro='Debian GNU/Linux 11 (bullseye)',
                distro_release='bullseye',
                image_id='sha256:ba9a86c8195c9eba8504720144d22e39736d61dcaf119e328948b4b96f118b29',
                package_types={
                    'mariadb-10.5@1:10.5.15-0+deb11u1': 'os'}
            ),
            'link': 'https://security-tracker.debian.org/tracker/CVE-2022-32091',
            'cvss': 9.8,
            'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
            'description': 'MariaDB v10.7 was discovered to contain an use-after-poison in in __interceptor_memset at /libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc.',
            'risk_factors': ['Attack complexity: low', 'Attack vector: network', 'Critical severity', 'Recent vulnerability'],
            'published_date': '2022-07-01T23:15:00+03:00',
            'lowest_fixed_version': 'N/A',
            'fixed_versions': [],
            'licenses': 'Unknown'}
        record = Record(
            check_id=f"CKV_{cve_id.replace('-', '_')}",
            bc_check_id=f"BC_{cve_id.replace('-', '_')}",
            check_name="SCA package scan",
            check_result={"result": CheckResult.FAILED},
            code_block=[(0,"mariadb-10.5: 7.74.0-1.3+deb11u1")],
            file_path=f"/{file_abs_path}",
            file_line_range=[0, 0],
            resource=f'{file_abs_path}.mariadb-10.5',
            check_class='checkov.common.bridgecrew.vulnerability_scanning.image_scanner.ImageScanner',
            evaluations=None,
            file_abs_path=file_abs_path.split(' ')[0],
            severity=Severities.get(BcSeverities.CRITICAL),
            vulnerability_details=details,
        )
        extra_resource = ExtraResource(
            file_abs_path=file_abs_path,
            file_path=f"/{rootless_file_path}",
            resource=f"{file_abs_path}.requests",
            vulnerability_details={
                "package_name": "requests",
                "package_version": "",
                'licenses': "",
            }
        )

        report.add_record(record)
        report.extra_resources.add(extra_resource)
        csv_sbom_report.add_report(report=report, git_org="acme", git_repository="bridgecrewio/example")

        # when
        csv_sbom_report.persist_report_container_images(file_name=file_name, is_api_key=True, output_path=str(tmp_path))

        # then
        output_file_path = tmp_path / file_name
        csv_output = output_file_path.read_text()
        csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_IMAGE)
        expected_csv = (
            "Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses\n"
            "mariadb-10.5,1:10.5.15-0+deb11u1,/example/Dockerfile (sha256:ba9a86c8195c9eba8504720144d22e39736d61dcaf119e328948b4b96f118b29),acme,bridgecrewio/example,CVE-2022-32091,CRITICAL,Unknown\n"
            "requests,,/Dockerfile (sha256:ba9a86c8195c9eba8504720144d22e39736d61dcaf119e328948b4b96f118b29),acme,bridgecrewio/example,,,\n"
        )

        assert csv_output == expected_csv

        expected_csv = (
            "Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses\n"
            "\"mariadb-10.5\",1:10.5.15-0+deb11u1,/example/Dockerfile (sha256:ba9a86c8195c9eba8504720144d22e39736d61dcaf119e328948b4b96f118b29),acme,bridgecrewio/example,CVE-2022-32091,CRITICAL,\"Unknown\"\n"
            "\"requests\",,/Dockerfile (sha256:ba9a86c8195c9eba8504720144d22e39736d61dcaf119e328948b4b96f118b29),acme,bridgecrewio/example,,,\"\"\n"
        )

        assert csv_output_str == expected_csv

    def test_sca_package_csv_output_with_licenses(self, tmp_path: Path):
        # given
        file_name = "oss_packages.csv"
        csv_sbom_report = CSVSBOM()
        report = Report(CheckType.SCA_PACKAGE)

        cve_id = "CVE-2019-1010083"
        rootless_file_path = "requirements.txt"
        file_abs_path = f"example/{rootless_file_path}"

        details = {
            "id": cve_id,
            "severity": "high",
            "package_name": "flask",
            "package_version": "0.6",
            "licenses": "MIT"
        }
        record = Record(
            check_id=f"CKV_{cve_id.replace('-', '_')}",
            bc_check_id=f"BC_{cve_id.replace('-', '_')}",
            check_name="SCA package scan",
            check_result={"result": CheckResult.FAILED},
            code_block=[(0,"")],
            file_path=f"/{rootless_file_path}",
            file_line_range=[0, 0],
            resource="requirements.txt.flask",
            check_class="",
            evaluations=None,
            file_abs_path=file_abs_path,
            severity=Severities.get(BcSeverities.HIGH),
            vulnerability_details=details,
        )
        extra_resource = ExtraResource(
            file_abs_path=file_abs_path,
            file_path=f"/{rootless_file_path}",
            resource=f"{rootless_file_path}.requests",
            vulnerability_details={
                "package_name": "requests",
                "package_version": "",
                "licenses": "MIT, Apache"
            }
        )

        report.add_record(record)
        report.extra_resources.add(extra_resource)
        csv_sbom_report.add_report(report=report, git_org="acme", git_repository="bridgecrewio/example")

        # when
        csv_sbom_report.persist_report_oss_packages(file_name=file_name, is_api_key=True, output_path=str(tmp_path))

        # then
        output_file_path = tmp_path / file_name
        csv_output = output_file_path.read_text()
        csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_PACKAGE)
        expected_csv = (
            "Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses\n"
            "flask,0.6,/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,MIT\n"
            "requests,,/requirements.txt,acme,bridgecrewio/example,,,\"MIT, Apache\"\n"
        )

        assert csv_output == expected_csv

        expected_csv = (
            "Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses\n"
            "\"flask\",0.6,/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,\"MIT\"\n"
            "\"requests\",,/requirements.txt,acme,bridgecrewio/example,,,\"MIT, Apache\"\n"
        )

        assert csv_output_str == expected_csv

    def test_print_iac_bom_reports(self, tmp_path: Path):
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/../runner_registry/example_s3_tf"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)
        output_types = ["cyclonedx", "csv"]
        output_path = tmp_path

        result_files_list = runner_registry.print_iac_bom_reports(output_path=str(output_path),
                                                                  scan_reports=reports,
                                                                  output_types=output_types)

        assert len(result_files_list) == len(output_types)
        for result_file in result_files_list.values():
            assert os.path.exists(result_file)
