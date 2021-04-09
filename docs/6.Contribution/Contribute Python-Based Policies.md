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

Define a policy as described [here](https://www.checkov.io/3.Custom%20Policies/Python%20Custom%20Policies.html).

## Example
`checkov/terraform/checks/resource/aws/APIGatewayCacheEnable.py`

```python
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class APIGatewayCacheEnable(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure API Gateway caching is enabled"
        id = "CKV_AWS_120"
        supported_resources = ['aws_api_gateway_stage']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "cache_cluster_enabled"


check = APIGatewayCacheEnable()
```

# Testing

Assuming the implemented check’s class is file is found in checkov/terraform/checks/<type>/<provider> directory, named <ClassName>.py, create an appropriate unit test file in tests/terraform/checks/<type>/<provider> directory, named test_<ClassName>.py.

The test suite should cover different check results; Test if the check outputs PASSED on a compliant configuration, and test if it output FAILED on a non-compliant configuration. You are also encouraged to test more specific components of the check, according to their complexity.


## Example

`tests/terraform/checks/resource/aws/test_APIGatewayCacheEnable.py`
```python
import unittest
import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.APIGatewayCacheEnable import check


class TestAPIGatewayCacheEnable(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                    resource "aws_api_gateway_rest_api" "example" {                    
                      name = "example"
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_api_gateway_rest_api']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "aws_api_gateway_rest_api" "example" {                    
                      name                  = "example"
                      cache_cluster_enabled = true
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_api_gateway_rest_api']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
```

