import unittest

import git
import os
import shutil

from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner

current_dir = os.path.dirname(os.path.realpath(__file__))
git_dir = "{}/projects".format(current_dir)
terragoat_dir = "{}/terragoat".format(git_dir)
cfngoat_dir = "{}/cfngoat".format(git_dir)


class TestTerragoat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        git.Git(git_dir).clone("git@github.com:bridgecrewio/terragoat.git")
        git.Git(git_dir).clone("git@github.com:bridgecrewio/cfngoat.git")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(terragoat_dir)
        shutil.rmtree(cfngoat_dir)

    def test_terragoat(self):
        runner_filter = RunnerFilter(framework="terraform", checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(banner, runner_filter, tf_runner(), cfn_runner(), k8_runner())
        reports = runner_registry.run(root_folder=terragoat_dir)
        terraform_checkov_report = reports[0]
        self.assertGreaterEqual(len(terraform_checkov_report.failed_checks), 35)
        self.assertGreaterEqual(len(terraform_checkov_report.passed_checks), 29)
        self.assertEqual(len(terraform_checkov_report.parsing_errors), 0)

    def test_cfngoat(self):
        runner_filter = RunnerFilter(framework="cloudformation", checks=None, skip_checks=None)
        runner_registry = RunnerRegistry(banner, runner_filter, tf_runner(), cfn_runner(), k8_runner())
        reports = runner_registry.run(root_folder=cfngoat_dir)
        terraform_checkov_report = reports[0]
        self.assertGreaterEqual(len(terraform_checkov_report.failed_checks), 19)
        self.assertGreaterEqual(len(terraform_checkov_report.passed_checks), 16)
        self.assertEqual(len(terraform_checkov_report.parsing_errors), 0)



if __name__ == '__main__':
    unittest.main()
