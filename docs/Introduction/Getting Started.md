# Getting Started

The installation is quick and straightforward - install, configure input & scan.


```bash
# install from pypi using pip
pip install checkov


# select an input folder that contains your terraform plan files
checkov -d /user/tf
```

## Scan result sample (CLI)

```bash
Passed Checks: 1, Failed Checks: 1, Suppressed Checks: 0

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/main.tf:
	 Passed for resource: aws_s3_bucket.template_bucket 

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/../regionStack/main.tf:
	 Failed for resource: aws_s3_bucket.sls_deployment_bucket_name       
```

## Export scan to JSON

```bash
checkov -d /user/tf -o json
```

Sample output

```json
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

## Sample policy

Each Checkov policy is defined by resources it scans and expected values for related resource blocks.

For example, a policy that ensures all data is stored in S3 is versioned, scans the `versioning` configuration for all `aws_s3_bucket` supported resources. The ```scan_resource_conf`is a method that defines the scan's expectyed behavior, i.e.`versioning_block['enabled']``

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

## What's Next?
From this point, you can head to the [Policies](policies.md) for further examples or the How-to Guides section if you’re ready to get your hands dirty.


## 
