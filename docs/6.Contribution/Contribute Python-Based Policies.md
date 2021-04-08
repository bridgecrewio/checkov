---
layout: default
published: true
title: Contribute Python-Based Policies
nav_order: 2
---

# Contributing Python-based Custom Policies

After identifying a Custom Policy's IaC type and provider, place the file with its code in `checkov/<scanner>/checks/<type>/<provider>`, where **type ** is the Custom Policy's type and **provider** is the Custom Policy's provider.

A Custom Policy is a class implementing an abstract base class that corresponds to some provider and type.

For example, all Custom Policies of **resource** type and **aws **provider implement the resource base class found at `checkov/terraform/checks/resource/base_check.py`. The resource check needs to implement its base abstract method named `scan_resource_conf`, which accepts as an input a dictionary of all the key-valued resource attributes, and outputs a CheckResult.

Define a policy as described [here](../3.Custom%20Policies/Python%20Custom%20Policies.md).

## Example
`checkov/terraform/checks/resource/aws/APIGatewayCacheEnable.py`

[block:code]
{
  "codes": [
    {
      "code": "from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck\nfrom checkov.common.models.enums import CheckCategories\n\n\nclass APIGatewayCacheEnable(BaseResourceValueCheck):\n\n    def __init__(self):\n        name = \"Ensure API Gateway caching is enabled\"\n        id = \"CKV_AWS_120\"\n        supported_resources = ['aws_api_gateway_stage']\n        categories = [CheckCategories.BACKUP_AND_RECOVERY]\n        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)\n\n    def get_inspected_key(self):\n        return \"cache_cluster_enabled\"\n\n\ncheck = APIGatewayCacheEnable()",
      "language": "python",
      "name": " "
    }
  ]
}
[/block]

# Testing

Assuming the implemented check’s class is file is found in checkov/terraform/checks/<type>/<provider> directory, named <ClassName>.py, create an appropriate unit test file in tests/terraform/checks/<type>/<provider> directory, named test_<ClassName>.py.

The test suite should cover different check results; Test if the check outputs PASSED on a compliant configuration, and test if it output FAILED on a non-compliant configuration. You are also encouraged to test more specific components of the check, according to their complexity.


## Example

`tests/terraform/checks/resource/aws/test_APIGatewayCacheEnable.py`

[block:code]
{
  "codes": [
    {
      "code": "import unittest\nimport hcl2\n\nfrom checkov.common.models.enums import CheckResult\nfrom checkov.terraform.checks.resource.aws.APIGatewayCacheEnable import check\n\n\nclass TestAPIGatewayCacheEnable(unittest.TestCase):\n\n    def test_failure(self):\n        hcl_res = hcl2.loads(\"\"\"\n                    resource \"aws_api_gateway_rest_api\" \"example\" {                    \n                      name = \"example\"\n                    }\n                \"\"\")\n        resource_conf = hcl_res['resource'][0]['aws_api_gateway_rest_api']['example']\n        scan_result = check.scan_resource_conf(conf=resource_conf)\n        self.assertEqual(CheckResult.FAILED, scan_result)\n\n    def test_success(self):\n        hcl_res = hcl2.loads(\"\"\"\n                    resource \"aws_api_gateway_rest_api\" \"example\" {                    \n                      name                  = \"example\"\n                      cache_cluster_enabled = true\n                    }\n                \"\"\")\n        resource_conf = hcl_res['resource'][0]['aws_api_gateway_rest_api']['example']\n        scan_result = check.scan_resource_conf(conf=resource_conf)\n        self.assertEqual(CheckResult.PASSED, scan_result)\n\nif __name__ == '__main__':\n    unittest.main()",
      "language": "python",
      "name": " "
    }
  ]
}
[/block]
