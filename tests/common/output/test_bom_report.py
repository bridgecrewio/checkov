import logging
import os
import io
import sys
from pathlib import Path
from unittest.mock import patch
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner

logger = logging.getLogger()
logger.level = logging.INFO


class TestBomOutput:
    def test_iac_csv_output(self, tmp_path: Path):
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/../runner_registry/example_s3_tf"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)

        with patch('sys.stdout', new=io.StringIO()) as captured_output:
            try:
                stream_handler = logging.StreamHandler(sys.stdout)
                logger.addHandler(stream_handler)
                runner_registry.print_iac_bom_reports(output_path=str(tmp_path),
                                                      scan_reports=reports,
                                                      output_types=['csv'],
                                                      account_id="org/name")
            finally:
                logger.removeHandler(stream_handler)

        output = captured_output.getvalue()
        assert 'Persisting SBOM to' in output
        iac_file_path = tmp_path / 'results_iac.csv'
        with open(iac_file_path) as file:
            content = file.readlines()
            header = content[:1][0]
            assert 'Resource,Path,Git Org,Git Repository,Misconfigurations,Severity,Policy title,Guideline\n' == header
            rows = content[1:]
            assert 'aws_s3_bucket' in rows[0]

    def test_sca_package_csv_output(self, tmp_path: Path):
        """
        tests for sca_package cvs are located in:
        tests/sca_package/test_output_reports.py
        """
        assert True

    def test_sca_image_csv_output(self, tmp_path: Path):
        """
        tests for sca_image cvs are located in:
        tests/sca_image/test_output_reports.py
        """
        assert True

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
                                                                  output_types=output_types,
                                                                  account_id="org/name")

        assert len(result_files_list) == len(output_types)
        for result_file in result_files_list.values():
            assert os.path.exists(result_file)
