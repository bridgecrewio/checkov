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
Passed checks: 7, Failed checks: 15, Skipped checks: 2

Check: "S3 Bucket has an ACL defined which allows public access."
	PASSED for resource: aws_s3_bucket.sls_deployment_bucket_name
	File: /../regionStack/main.tf:23-32

Check: "Ensure the S3 bucket has access logging enabled"
	FAILED for resource: aws_s3_bucket.template_bucket
	File: /main.tf:81-92

		81 | resource "aws_s3_bucket" "template_bucket" {
		82 |   region        = var.region
		83 |   bucket        = local.bucket_name
		84 |   # checkov:skip=CKV_AWS_19:Honestly dear, I don't give a damn
		85 |   # checkov:skip=CKV_AWS_20
		86 |   acl           = "public-read"
		87 |   force_destroy = true
		88 | 
		89 |   tags = {
		90 |     Name = "${local.bucket_name}-${data.aws_caller_identity.current.account_id}"
		91 |   }
		92 | }

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
	SKIPPED for resource: aws_s3_bucket.template_bucket
	Suppress comment: Honestly dear, I don't give a damn
	File: /main.tf:81-92       
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
                "check_id": "CKV_AWS_20",
                "check_name": "S3 Bucket has an ACL defined which allows public access.",
                "check_result": {
                    "result": "PASSED"
                },
                "code_block": [
                    [
                        23,
                        "resource \"aws_s3_bucket\" \"sls_deployment_bucket_name\" {\n"
                    ],
                    [
                        24,
                        "  provider      = aws.current_region\n"
                    ],
                   ...
                ],
                "file_path": "/../regionStack/main.tf",
                "file_line_range": [
                    23,
                    32
                ],
                "resource": "aws_s3_bucket.sls_deployment_bucket_name",
                "check_class": "checkov.terraform.checks.resource.aws.S3PublicACL"
            }
        ],
        "failed_checks": [
            {
                "check_id": "CKV_AWS_18",
                "check_name": "Ensure the S3 bucket has access logging enabled",
                "check_result": {
                    "result": "FAILED"
                },
                "code_block": [
                    [
                        81,
                        "resource \"aws_s3_bucket\" \"template_bucket\" {\n"
                    ],
                    [
                        82,
                        "  region        = var.region\n"
                    ],
                    [
                        83,
                        "  bucket        = local.bucket_name\n"
                    ],
                    [
                        84,
                        "  # checkov:skip=CKV_AWS_19:Honestly dear, I don't give a damn\n"
                    ],
                    [
                        85,
                        "  # checkov:skip=CKV_AWS_20\n"
                    ],
                    [
                        86,
                        "  acl           = \"public-read\"\n"
                    ],
                    [
                        87,
                        "  force_destroy = true\n"
                    ],
                    [
                        88,
                        "\n"
                    ],
                    [
                        89,
                        "  tags = {\n"
                    ],
                    [
                        90,
                        "    Name = \"${local.bucket_name}-${data.aws_caller_identity.current.account_id}\"\n"
                    ],
                    [
                        91,
                        "  }\n"
                    ],
                    [
                        92,
                        "}\n"
                    ]
                ],
                "file_path": "/main.tf",
                "file_line_range": [
                    81,
                    92
                ],
                "resource": "aws_s3_bucket.template_bucket",
                "check_class": "checkov.terraform.checks.resource.aws.S3AccessLogs"
            },
            {
                "check_id": "CKV_AWS_21",
                "check_name": "Ensure all data stored in the S3 bucket have versioning enabled",
                "check_result": {
                    "result": "FAILED"
                },
                "code_block": [
                    [
                        81,
                        "resource \"aws_s3_bucket\" \"template_bucket\" {\n"
                    ],
                    [
                        82,
                        "  region        = var.region\n"
                    ],
                    ...
                ],
                "file_path": "/main.tf",
                "file_line_range": [
                    81,
                    92
                ],
                "resource": "aws_s3_bucket.template_bucket",
                "check_class": "checkov.terraform.checks.resource.aws.S3Versioning"
            },
           
        ],
        "skipped_checks": [
            {
                "check_id": "CKV_AWS_19",
                "check_name": "Ensure all data stored in the S3 bucket is securely encrypted at rest",
                "check_result": {
                    "result": "SKIPPED",
                    "suppress_comment": "Honestly dear, I don't give a damn"
                },
                "code_block": [
                    [
                        81,
                        "resource \"aws_s3_bucket\" \"template_bucket\" {\n"
                    ],
                    [
                        82,
                        "  region        = var.region\n"
                    ],
                    ...
                ],
                "file_path": "/main.tf",
                "file_line_range": [
                    81,
                    92
                ],
                "resource": "aws_s3_bucket.template_bucket",
                "check_class": "checkov.terraform.checks.resource.aws.S3Encryption"
            }
        ],
        "parsing_errors": []
    },
    "summary": {
        "passed": 1,
        "failed": 2,
        "skipped": 1,
        "parsing_errors": 0,
        "checkov_version": "1.0.63"
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
        name = "Ensure all data stored in the S3 bucket have versioning enabled"
        id = "CKV_AWS_21"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
    def scan_resource_conf(self, conf):
        """
            Looks for logging configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'versioning' in conf.keys():
            versioning_block = conf['versioning'][0]
            if versioning_block['enabled'][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED
scanner = S3Versioning()
```

## What's Next?
From this point, you can head to the [Policies](policies.md) for further examples or the How-to Guides section if you’re ready to get your hands dirty.


## 
