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
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner


class TestBomOutput:
    def test_csv_output(self, tmp_path: Path):
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
            assert 'Resource,Path,git org,git repository,Misconfigurations,Severity\n' == header
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
        csv_output_str = csv_sbom_report.get_csv_output_oss_packages()
        expected_csv = (
            "Package,Version,Path,git org,git repository,Vulnerability,Severity,License\n"
            "flask,0.6,/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,\n"
            "requests,,/requirements.txt,acme,bridgecrewio/example,,,\n"
        )

        assert csv_output == expected_csv
        assert csv_output_str == expected_csv
