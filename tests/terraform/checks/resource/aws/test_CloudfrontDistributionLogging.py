import os
import unittest

import pytest

from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.CloudfrontDistributionLogging import check
from checkov.terraform.runner import Runner


class TestCloudfrontDistributionLogging(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "comment": "Example",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "comment": "Example",
            "logging_config": [
                {
                    "bucket": "some-arn"
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    @pytest.mark.skip("Need to handle null variables")
    def test_null_var_651(self):
        self.skipTest("Need to handle null variables")
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir,
                                      "../../../parser/resources/parser_scenarios/null_variables_651")
        valid_dir_path = os.path.normpath(valid_dir_path)
        runner = Runner()
        checks_allowlist = ['CKV_AWS_86']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allowlist))
        self.assertEqual(len(report.failed_checks), 1)
        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)


if __name__ == '__main__':
    unittest.main()
