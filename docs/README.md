# Checkov

----

[![Maintained by Bridgecrew.io](https://img.shields.io/badge/maintained%20by-bridgecrew.io-blueviolet)](https://bridgecrew.io)
[![build status](https://github.com/bridgecrewio/terraform-static-analysis/workflows/build/badge.svg)](https://github.com/bridgecrewio/terraform-static-analysis/actions?query=workflow%3Abuild) 
![code_coverage](coverage.svg) <!--- coverage is auto generated in the build workflow -->
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

## **Table of contents**

- [Description](#description)
- [Features](#features)
- [Demo](#demo)
- [Getting Started](#getting-started)
- [Support](#Support)
- [Contributing](#contributing)

## Description

Checkov is a static code analysis tool for infrastructure-as-code. It scans cloud infrastructure provisioned using Terraform and detects security and compliance misconfigurations. 

Checkov is written in Python and provides a simple method to write and manage policies. It follows the CIS Foundations benchmarks where applicable.

 ## Features

 * 40+ built-in policies cover security and compliance best practices for AWS, Azure & Google Cloud.
 * Policies support variable scanning by building a dynamic code dependency graph.
 * Supports in-line suppression of accepted risks or false-positives to reduce recurring scan failures.
 * Output currently available as CLI, JSON or JUnit XML.

## Demo

***TODO(GIF)

## Getting Started

### Installation

```python
pip install checkov
```

### Configure an input folder

```python
checkov -d /user/tf
```

### Scan result sample (CLI)

```python
Passed Checks: 1, Failed Checks: 1, Suppressed Checks: 0

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/main.tf:
	 Passed for resource: aws_s3_bucket.template_bucket 

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/../regionStack/main.tf:
	 Failed for resource: aws_s3_bucket.sls_deployment_bucket_name       
```

### Export scan to JSON

```python
checkov -d /user/tf -o json
```

Sample output

```python
{
    "results": {
        "passed_checks": [
            {
                "check_id": "BC_AWS_S3_14",
                "check_name": "Ensure all data stored in the S3 bucket is securely encrypted at rest",
                "check_result": "SUCCESS",
                "code_block": "",
                "file_path": "/main.tf",
                "file_line_range": "",
                "resource": "aws_s3_bucket.template_bucket"
            },
            {
                "check_id": "BC_AWS_S3_13",
                "check_name": "Ensure the S3 bucket has access logging enabled",
                "check_result": "SUCCESS",
                "code_block": "",
                "file_path": "/main.tf",
                "file_line_range": "",
                "resource": "aws_s3_bucket.template_bucket"
            }
                  ],
        "suppressed_checks": [],
        "parsing_errors": []
    },
    "summary": {
        "passed": 2,
        "failed": 0,
        "suppressed": 0,
        "parsing_errors": 0
    }
}
```

### Sample policy

Each policy is defined by resources it scans and expected values for related resource blocks. 

For example, a policy that ensures all data is stored in S3 is versioned, scans the ``versioning`` configuration for all ``aws_s3_bucket`` supported resources. The ```scan_resource_conf`` is a method that defines the scan's expectyed behavior, i.e. ``versioning_block['enabled']``

```python
from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck
class S3Versioning(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket is versioned"
        id = "S3_11"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
    def scan_resource_conf(self, conf):
        if 'versioning' in conf.keys():
            versioning_block = conf['versioning'][0]
            if versioning_block['enabled'][0]:
                return CheckResult.SUCCESS
        return CheckResult.FAILURE
scanner = S3Versioning()
```

## Alternatives

For Terraform compliance scanners check out [tfsec](https://github.com/liamg/tfsec), [Terrascan](https://github.com/cesar-rodriguez/terrascan) and [Terraform AWS Secure Baseline](https://github.com/nozaq/terraform-aws-secure-baseline)

For CloudFormaiton scanning check out Skyscanner's [cfripper](https://github.com/Skyscanner/cfripper/) and [cfn_nag](https://github.com/stelligent/cfn_nag)

## Support

Bridgecrew builds and maintains Checkov to make policy-as-code simple and accessible. Policies defined as code ensure that secure infrastructure provisioning becomes maintainable, versioned, testable and transparent.

If you need support contact us at support@bridgecrew.io or [Open a ticket](
