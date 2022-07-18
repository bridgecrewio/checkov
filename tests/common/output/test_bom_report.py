import unittest

import os
import io
from unittest.mock import patch
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner
from pathlib import Path
from checkov.common.output.cyclonedx import CycloneDX
import re


class TestBomOutput(unittest.TestCase):
    def test_csv_output(self):
        test_files_dir = os.path.dirname(os.path.realpath(__file__)) + "/../runner_registry/example_s3_tf"
        runner_filter = RunnerFilter(framework=None, checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(
            banner, runner_filter, tf_runner(), cfn_runner(), k8_runner()
        )
        reports = runner_registry.run(root_folder=test_files_dir)

        with patch('sys.stdout', new=io.StringIO()) as captured_output:
            runner_registry.print_bom_reports(output_path="/tmp", scan_reports=reports, output_types=['csv'])

        output = captured_output.getvalue()

        self.assertIn('Persisting SBOM to ', output)
        iac_file_path = re.search("Persisting SBOM to (.*iac.csv)", output).group(1)
        with open(iac_file_path) as file:
            content = file.readlines()
            header = content[:1][0]
            self.assertEqual('Resource,Path,git org,git repository,Misconfigurations,Severity\n', header)
            rows = content[1:]
            self.assertIn('aws_s3_bucket', rows[0])
        oss_file_path = re.search("Persisting SBOM to (.*oss_packages.csv)", output).group(1)
        with open(oss_file_path) as file:
            content = file.readlines()
            header = content[:1][0]
            self.assertEqual('Package,Version,Path,git org,git repository,Vulnerability,Severity,License\n', header)
            row = content[1:][0]
            self.assertIn('bridgecrew.cloud', row)
