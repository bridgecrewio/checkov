import os
import unittest
from typing import List, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.cloudformation.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.runner_filter import RunnerFilter



class CFNBaseResourceCheck(BaseResourceCheck):

    def __init__(self):
        name = "Cloudformation test"
        id = "CKV_AWS_0"
        supported_resources = ['AWS::ElasticLoadBalancingV2::LoadBalancer']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline="Cloudformation guideline")

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED

class CFNBaseResourceValueCheck(BaseResourceValueCheck):

    def __init__(self):
        name = "Cloudformation test"
        id = "CKV_AWS_0"
        supported_resources = ['AWS::ElasticLoadBalancingV2::LoadBalancer']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline="Cloudformation guideline")

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED

class CFNBaseResourceNegativeValueCheck(BaseResourceNegativeValueCheck):

    def __init__(self):
        name = "Cloudformation test"
        id = "CKV_AWS_0"
        supported_resources = ['AWS::ElasticLoadBalancingV2::LoadBalancer']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline="Cloudformation guideline")

    def get_forbidden_values(self) -> List[Any]:
        return ["routing.http.drop_invalid_header_fields.enabled"]

    def get_inspected_key(self) -> str:
        return "false"

class CFNBaseCloudsplainingIAMCheck(BaseCloudsplainingIAMCheck):

    def __init__(self) -> None:
        name = "Cloudformation test"
        id = "CKV_AWS_0"
        super().__init__(name=name, id=id, guideline="Cloudformation guideline")

    def cloudsplaining_analysis(self, policy):
        return []

class TestGuidelines(unittest.TestCase):

    def test_CFNBaseResourceCheck(self):
        expected = "Cloudformation guideline"
        runner = cfn_runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        check = CFNBaseResourceCheck()
        test_files_dir = current_dir + "/aws/example_ALBDropHttpHeaders"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertEqual(report.passed_checks[0].guideline, expected)

    def test_CFNBaseResourceValueCheck(self):
        expected = "Cloudformation guideline"
        runner = cfn_runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        check = CFNBaseResourceCheck()
        test_files_dir = current_dir + "/aws/example_ALBDropHttpHeaders"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertEqual(report.passed_checks[0].guideline, expected)

    def test_CFNBaseResourceNegativeValueCheck(self):
        expected = "Cloudformation guideline"
        runner = cfn_runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        check = CFNBaseResourceNegativeValueCheck()
        test_files_dir = current_dir + "/aws/example_ALBDropHttpHeaders"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertEqual(report.passed_checks[0].guideline, expected)


    def test_CFNBaseCloudsplainingIAMCheck(self):
        expected = "Cloudformation guideline"
        runner = cfn_runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        check = CFNBaseCloudsplainingIAMCheck()
        test_files_dir = current_dir + "/aws/Cloudsplaining_IAMCredentialsExposure"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertEqual(report.passed_checks[0].guideline, expected)

if __name__ == '__main__':
    unittest.main()
