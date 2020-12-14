import os
import unittest

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.cloudformation.checks.resource.registry import cfn_registry as registry
from checkov.serverless.runner import Runner
from checkov.runner_filter import RunnerFilter


class ServerlessCheck(BaseResourceCheck):

    def __init__(self):
        name = "Serverless test"
        id = "CKV_T_1"
        supported_resources = ['AWS::S3*']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED


class TestWildcardEntities(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        check = ServerlessCheck()

        test_files_dir = current_dir + "/example_WildcardEntities"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        registry.wildcard_checks['AWS::S3*'].remove(check)

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
