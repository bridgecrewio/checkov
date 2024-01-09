import os
import unittest

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.resource.registry import resource_registry as registry
from checkov.terraform.runner import Runner
from checkov.runner_filter import RunnerFilter


class TerraformCheck(BaseResourceCheck):

    def __init__(self):
        name = "Terraform test"
        id = "CKV_T_1"
        supported_resources = ['aws_iam_*', 'null_resource', '*s3*']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED


class TestWildcardEntities(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        check = TerraformCheck()

        test_files_dir = current_dir + "/example_WildcardEntities"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        registry.wildcard_checks['aws_iam_*'].remove(check)
        registry.checks['null_resource'].remove(check)

        registry.wildcard_checks['*s3*'].remove(check)
        
        del registry.checks['null_resource']
        del registry.wildcard_checks['*s3*']
        del registry.wildcard_checks['aws_iam_*']
        # Only for resource and nof for data "aws_iam_policy_document"
        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
