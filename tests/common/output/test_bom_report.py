import pytest
import pathlib

import os
import io
from unittest.mock import patch
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner


class TestBomOutput:
    def test_csv_output(self, tmp_path: pathlib.Path):
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
