import os
import unittest

import dpath

from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.definition_access import TerraformDefinitionAccess
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.runner import Runner


DIR = os.path.dirname(os.path.realpath(__file__))


class PolicyToBucketByName(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Make sure the bucket can be found for the policy",
            id="PolicyToBucketByName",
            categories=[],
            supported_resources=["aws_s3_bucket_policy"])

    def scan_resource_conf(self, conf, entity_type, entity_name, definition_access):
        assert isinstance(definition_access, TerraformDefinitionAccess)     # verify type

        # TODO: don't think the parser resolves ".id" references
        # bucket_ref = conf["bucket"]
        # assert bucket_ref == "my_bucket"

        bucket_conf = definition_access.find_resource_by_name("aws_s3_bucket", "my_bucket")
        assert dpath.get(bucket_conf, "bucket/0") == "mybucket.us-east-1.mycompany.com", bucket_conf
        return CheckResult.PASSED


class PolicyToBucketByValue(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Make sure the bucket can be found for the policy",
            id="PolicyToBucketByValue",
            categories=[],
            supported_resources=["aws_s3_bucket_policy"])

    def scan_resource_conf(self, conf, entity_type, entity_name, definition_access):
        assert isinstance(definition_access, TerraformDefinitionAccess)     # verify type

        count = 0
        for bucket_conf in definition_access.find_resources_by_attribute("aws_s3_bucket", "bucket/0",
                                                                         "mybucket.us-east-1.mycompany.com"):
            assert dpath.get(bucket_conf, "bucket/0") == "mybucket.us-east-1.mycompany.com", bucket_conf
            count += 1

        assert count == 1
        return CheckResult.PASSED


class BackwardsCompat1Check(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Making sure the original scan_resource_conf signature still works",
            id="BackwardsCompat1Check",
            categories=[],
            supported_resources=["aws_s3_bucket_policy", "aws_s3_bucket"])

    # Old signature - any call indicates success
    def scan_resource_conf(self, conf):
        return CheckResult.PASSED


class BackwardsCompat2Check(BaseResourceCheck):
    def __init__(self):
        super().__init__(
            name="Making sure the original scan_resource_conf signature still works",
            id="BackwardsCompat2Check",
            categories=[],
            supported_resources=["aws_s3_bucket_policy", "aws_s3_bucket"])

    # Old, old signature - any call indicates success
    def scan_resource_conf(self, conf, entity_type):
        return CheckResult.PASSED


class TestResourceCorrelation(unittest.TestCase):
    # This will install a custom check, so setUp/tearDown will ensure the check list is unchanged
    # globally by our changes.
    def setUp(self) -> None:
        self.check_list_before = resource_registry.checks.copy()     # copy
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()
        resource_registry.checks = self.check_list_before
        self.check_list_before = None

    def test_backwards_compat1(self):
        self._do_run_expect_pass(BackwardsCompat1Check())

    def test_backwards_compat2(self):
        self._do_run_expect_pass(BackwardsCompat2Check())

    def test_policy_to_bucket_by_name(self):
        self._do_run_expect_pass(PolicyToBucketByName())

    def test_policy_to_bucket_by_value(self):
        self._do_run_expect_pass(PolicyToBucketByValue())


    def _do_run_expect_pass(self, check):
        report = Runner().run(root_folder=f"{DIR}/resources/resource_correlation/tf",
                              runner_filter=RunnerFilter(checks=[check.id]))
        assert not report.failed_checks         # no results
        assert not report.skipped_checks        # no results
        assert not report.parsing_errors        # no results

        assert report.passed_checks
        assert not [r for r in report.passed_checks if r.check_id != check.id]
