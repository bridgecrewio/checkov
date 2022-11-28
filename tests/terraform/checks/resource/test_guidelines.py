import os
import unittest
from typing import List, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.terraform.runner import Runner as tf_runner
from checkov.runner_filter import RunnerFilter



class TFBaseResourceCheck(BaseResourceCheck):

    def __init__(self):
        name = "terraform test"
        id = "CKV_AWS_0"
        supported_resources = ['aws_api_gateway_method_settings']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline="terraform guideline")

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED

class TFBaseResourceValueCheck(BaseResourceValueCheck):

    def __init__(self):
        name = "terraform test"
        id = "CKV_AWS_0"
        supported_resources = ['aws_api_gateway_method_settings']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline="terraform guideline")

    def scan_resource_conf(self, conf):
        return CheckResult.PASSED

class TFBaseResourceNegativeValueCheck(BaseResourceNegativeValueCheck):

    def __init__(self):
        name = "terraform test"
        id = "CKV_AWS_0"
        supported_resources = ['aws_api_gateway_method_settings']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline="terraform guideline")

    def get_forbidden_values(self) -> List[Any]:
        return ["settings/[0]/data_trace_enabled"]

    def get_inspected_key(self) -> str:
        return [True]


class TestGuidelines(unittest.TestCase):

    def test_TFBaseResourceCheck(self):
        expected = "terraform guideline"
        runner = tf_runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        check = TFBaseResourceCheck()
        test_files_dir = current_dir + "/aws/example_APIGatewayMethodSettingsDataTrace"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertEqual(report.passed_checks[0].guideline, expected)

    def test_TFBaseResourceValueCheck(self):
        expected = "terraform guideline"
        runner = tf_runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        check = TFBaseResourceCheck()
        test_files_dir = current_dir + "/aws/example_APIGatewayMethodSettingsDataTrace"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertEqual(report.passed_checks[0].guideline, expected)

    def test_TFBaseResourceNegativeValueCheck(self):
        expected = "terraform guideline"
        runner = tf_runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        check = TFBaseResourceNegativeValueCheck()
        test_files_dir = current_dir + "/aws/example_APIGatewayMethodSettingsDataTrace"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertEqual(report.passed_checks[0].guideline, expected)



if __name__ == '__main__':
    unittest.main()
