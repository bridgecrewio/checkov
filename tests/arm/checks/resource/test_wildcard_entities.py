import os
import unittest

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.arm.registry import arm_resource_registry as registry
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class ArmCheck(BaseResourceCheck):

    def __init__(self):
        name = "Arm test"
        id = "CKV_T_1"
        supported_resources = ['Microsoft.KeyVault/vaults*', '*servers*']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED


class TestWildcardEntities(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        check = ArmCheck()

        test_files_dir = current_dir + "/example_WildcardEntities"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        registry.wildcard_checks['Microsoft.KeyVault/vaults*'].remove(check)
        registry.wildcard_checks['*servers*'].remove(check)

        # Only for resource and nof for data "aws_iam_policy_document"
        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
