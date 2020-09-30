---
layout: default
published: true
title: Getting Started
order: 2
---

# Getting Started

The installation is quick and straightforward - install, configure input & scan.


```bash
# install from pypi using pip
pip install checkov


# select an input folder that contains your terraform plan files
checkov -d /user/tf
```

## CLI Options
```bash
-h, --help            show this help message and exit
  -v, --version         version
  -d DIRECTORY, --directory DIRECTORY
                        IaC root directory (can not be used together with
                        --file).
  -f FILE, --file FILE  IaC file(can not be used together with --directory)
  --external-checks-dir EXTERNAL_CHECKS_DIR
                        Directory for custom checks to be loaded. Can be
                        repeated
  --external-checks-git EXTERNAL_CHECKS_GIT
                        Github url of external checks to be added. you can
                        specify a subdirectory after a double-slash //. cannot
                        be used together with --external-checks-dir
  -l, --list            List checks
  -o [{cli,json,junitxml,github_failed_only}], --output [{cli,json,junitxml,github_failed_only}]
                        Report output format
  --no-guide            do not fetch bridgecrew guide in checkov output report
  --quiet               in case of CLI output, display only failed checks
  --framework {cloudformation,terraform,kubernetes,serverless,arm,all}
                        filter scan to run only on a specific infrastructure
                        code frameworks
  --merging-behavior {union,override,override_if_present,copy_parent}
                        Change the behavior how --check and --skip-check are
                        merged with existing definitions inside a
                        configuration file. By default "override_if_present"
                        is used, which will ignore configuration files if you
                        specify --check or --skip-check. "override" will
                        completely ignore configuration files for --check and
                        --skip-check. This can be used to clear the selection
                        from existing configuration files. "union" will keep
                        the checks from the command line and the one defined
                        in configuration files. "copy_parent" ignore the
                        current configuration and use the parent instead. This
                        is not useful for command line but for disabling a
                        configuration permanently.
  --config-files CONFIG_FILES [CONFIG_FILES ...]
                        A list of additional configuration files. The files
                        are listed in increasing priority. Configuration files
                        automatically detected have lower priority, but can be
                        added here again. The arguments specified in the
                        command line still have higher priority.
  --ignore-config-files [IGNORE_CONFIG_FILES [IGNORE_CONFIG_FILES ...]]
                        Ignore some or all default configuration files. If you
                        just this option without additional arguments, all
                        default configuration files are ignored. If you pass
                        arguments, these are interpreted as the file names of
                        those files that should be ignored.
  --list-considered-config-files
                        If set, checkov will only show the locations of config
                        fies that it will consider. It list all the locations
                        that will be considered and the status of the file at
                        this location (valid, invalid, not present or some
                        other error). This will also consider --config-files
                        and --ignore-config-files.
  -c CHECK, --check CHECK
                        filter scan to run only on a specific check
                        identifier(allowlist), You can specify multiple checks
                        separated by comma delimiter. E.g.:
                        CKV_AWS_1,CKV_AWS_3 You may want to specify a
                        different --merging-behavior.
  --skip-check SKIP_CHECK
                        filter scan to run on all check but a specific check
                        identifier(denylist), You can specify multiple checks
                        separated by comma delimiter. E.g.:
                        CKV_AWS_1,CKV_AWS_3 You may want to specify a
                        different --merging-behavior.
  -s, --soft-fail       Runs checks but suppresses error code
  --bc-api-key BC_API_KEY
                        Bridgecrew API key
  --repo-id REPO_ID     Identity string of the repository, with form
                        <repo_owner>/<repo_name>
  -b BRANCH, --branch BRANCH
                        Selected branch of the persisted repository. Only has
                        effect when using the --bc-api-key flag. Defaults to
                        "master"

```

## Scan result sample (CLI)

Consider the following Terraform configuration of an S3 bucket:
```hcl-terraform
resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true

  tags = {
    Name = "foo-${data.aws_caller_identity.current.account_id}"
  }
  versioning {
    enabled = true
  }
  logging {
    target_bucket = "${aws_s3_bucket.log_bucket.id}"
    target_prefix = "log/"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.mykey.arn}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
  acl           = "private"
}
```
The appropriate output report is:

```bash
Passed checks: 4, Failed checks: 0, Skipped checks: 0

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "Ensure the S3 bucket has access logging enabled"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "Ensure all data stored in the S3 bucket have versioning enabled"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "S3 Bucket has an ACL defined which allows public access."
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25
```
The scanned bucket's configuration seems to comply with the available ``aws_s3_bucket`` resource type checks.

Suppose that now the bucket is used for static content hosting, and thus requires to configured with
allowed public access:
```hcl-terraform
resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true

  tags = {
    Name = "foo-${data.aws_caller_identity.current.account_id}"
  }
  versioning {
    enabled = true
  }
  logging {
    target_bucket = "${aws_s3_bucket.log_bucket.id}"
    target_prefix = "log/"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.mykey.arn}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
  acl           = "public-read"
}
data "aws_caller_identity" "current" {}

```
The output report would then contain the failed check:
```bash
Passed checks: 3, Failed checks: 1, Skipped checks: 0

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "Ensure the S3 bucket has access logging enabled"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "Ensure all data stored in the S3 bucket have versioning enabled"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "S3 Bucket has an ACL defined which allows public access."
	FAILED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25

		1 | resource "aws_s3_bucket" "foo-bucket" {
		2 |   region        = var.region
		3 |   bucket        = local.bucket_name
		4 |   force_destroy = true
		5 |
		6 |   tags = {
		7 |     Name = "foo-${data.aws_caller_identity.current.account_id}"
		8 |   }
		9 |   versioning {
		10 |     enabled = true
		11 |   }
		12 |   logging {
		13 |     target_bucket = "${aws_s3_bucket.log_bucket.id}"
		14 |     target_prefix = "log/"
		15 |   }
		16 |   server_side_encryption_configuration {
		17 |     rule {
		18 |       apply_server_side_encryption_by_default {
		19 |         kms_master_key_id = "${aws_kms_key.mykey.arn}"
		20 |         sse_algorithm     = "aws:kms"
		21 |       }
		22 |     }
		23 |   }
		24 |   acl           = "public-read"
		25 | }

```
The corresponding check would now fail, and the report will include the appropriate failing configuration
source code.

In order to skip the failed check, we annotate the bucket with a suppression comment (which needs to appear inside the resource scope):
```hcl-terraform
resource "aws_s3_bucket" "foo-bucket" {
  # checkov:skip=CKV_AWS_20:The bucket is a public static content host
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true
  tags = {
    Name = "foo-${data.aws_caller_identity.current.account_id}"
  }
  versioning {
    enabled = true
  }
  logging {
    target_bucket = "${aws_s3_bucket.log_bucket.id}"
    target_prefix = "log/"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.mykey.arn}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
  acl           = "public-read"
}
```

Checkov would then skip check ``CKV_AWS_20``, and the output report would be:

```bash
Passed checks: 3, Failed checks: 0, Skipped checks: 1

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "Ensure the S3 bucket has access logging enabled"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "Ensure all data stored in the S3 bucket have versioning enabled"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-25


Check: "S3 Bucket has an ACL defined which allows public access."
	SKIPPED for resource: aws_s3_bucket.foo-bucket
	Suppress comment: The bucket is a public static content host
	File: /example.tf:1-25
```

### Running a specific check(s)
To scan you directory with only a specific check use the `-c`\ `--check` flag. You can use multiple checks with comma `,` delimiter.
This is another way to skip execution of specific checks on a allowlist fashion

The following example will show results only for 2 scans (CKV_AWS_1 and CKV_AWS_2) :

```bash
checkov -d /user/tf --check CKV_AWS_1,CKV_AWS_2
```

## Export scan to JSON
For the sake of the example, we use the previous bucket configuration and disable it;s versioning is disabled for a check to fail.

```bash
checkov -d /user/tf -o json
```

Sample output
```json
{
    "results": {
        "passed_checks": [
            {
                "check_id": "CKV_AWS_19",
                "check_name": "Ensure all data stored in the S3 bucket is securely encrypted at rest",
                "check_result": {
                    "result": "PASSED"
                },
                "code_block": [
                    [
                        1,
                        "resource \"aws_s3_bucket\" \"foo-bucket\" {\n"
                    ],
                    [
                        2,
                        "  region        = var.region\n"
                    ],
                    [
                        3,
                        "  bucket        = local.bucket_name\n"
                    ],
                    [
                        4,
                        "  force_destroy = true\n"
                    ],
                    [
                        5,
                        "  #checkov:skip=CKV_AWS_20:The bucket is a public static content host\n"
                    ],
                    [
                        6,
                        "  tags = {\n"
                    ],
                    [
                        7,
                        "    Name = \"foo-${data.aws_caller_identity.current.account_id}\"\n"
                    ],
                    [
                        8,
                        "  }\n"
                    ],
                    [
                        9,
                        "  versioning {\n"
                    ],
                    [
                        10,
                        "    enabled = false\n"
                    ],
                    [
                        11,
                        "  }\n"
                    ],
                    [
                        12,
                        "  logging {\n"
                    ],
                    [
                        13,
                        "    target_bucket = \"${aws_s3_bucket.log_bucket.id}\"\n"
                    ],
                    [
                        14,
                        "    target_prefix = \"log/\"\n"
                    ],
                    [
                        15,
                        "  }\n"
                    ],
                    [
                        16,
                        "  server_side_encryption_configuration {\n"
                    ],
                    [
                        17,
                        "    rule {\n"
                    ],
                    [
                        18,
                        "      apply_server_side_encryption_by_default {\n"
                    ],
                    [
                        19,
                        "        kms_master_key_id = \"${aws_kms_key.mykey.arn}\"\n"
                    ],
                    [
                        20,
                        "        sse_algorithm     = \"aws:kms\"\n"
                    ],
                    [
                        21,
                        "      }\n"
                    ],
                    [
                        22,
                        "    }\n"
                    ],
                    [
                        23,
                        "  }\n"
                    ],
                    [
                        24,
                        "  acl           = \"public-read\"\n"
                    ],
                    [
                        25,
                        "}\n"
                    ]
                ],
                "file_path": "/example.tf",
                "file_line_range": [
                    1,
                    25
                ],
                "resource": "aws_s3_bucket.foo-bucket",
                "check_class": "checkov.terraform.checks.resource.aws.S3Encryption"
            },
            {
                "check_id": "CKV_AWS_18",
                "check_name": "Ensure the S3 bucket has access logging enabled",
                "check_result": {
                    "result": "PASSED"
                },
                "code_block": [
                    [
                        1,
                        "resource \"aws_s3_bucket\" \"foo-bucket\" {\n"
                    ],
                    [
                        2,
                        "  region        = var.region\n"
                    ],
                    [
                        3,
                        "  bucket        = local.bucket_name\n"
                    ],
                    [
                        4,
                        "  force_destroy = true\n"
                    ],
                    [
                        5,
                        "  #checkov:skip=CKV_AWS_20:The bucket is a public static content host\n"
                    ],
                    [
                        6,
                        "  tags = {\n"
                    ],
                    [
                        7,
                        "    Name = \"foo-${data.aws_caller_identity.current.account_id}\"\n"
                    ],
                    [
                        8,
                        "  }\n"
                    ],
                    [
                        9,
                        "  versioning {\n"
                    ],
                    [
                        10,
                        "    enabled = false\n"
                    ],
                    [
                        11,
                        "  }\n"
                    ],
                    [
                        12,
                        "  logging {\n"
                    ],
                    [
                        13,
                        "    target_bucket = \"${aws_s3_bucket.log_bucket.id}\"\n"
                    ],
                    [
                        14,
                        "    target_prefix = \"log/\"\n"
                    ],
                    [
                        15,
                        "  }\n"
                    ],
                    [
                        16,
                        "  server_side_encryption_configuration {\n"
                    ],
                    [
                        17,
                        "    rule {\n"
                    ],
                    [
                        18,
                        "      apply_server_side_encryption_by_default {\n"
                    ],
                    [
                        19,
                        "        kms_master_key_id = \"${aws_kms_key.mykey.arn}\"\n"
                    ],
                    [
                        20,
                        "        sse_algorithm     = \"aws:kms\"\n"
                    ],
                    [
                        21,
                        "      }\n"
                    ],
                    [
                        22,
                        "    }\n"
                    ],
                    [
                        23,
                        "  }\n"
                    ],
                    [
                        24,
                        "  acl           = \"public-read\"\n"
                    ],
                    [
                        25,
                        "}\n"
                    ]
                ],
                "file_path": "/example.tf",
                "file_line_range": [
                    1,
                    25
                ],
                "resource": "aws_s3_bucket.foo-bucket",
                "check_class": "checkov.terraform.checks.resource.aws.S3AccessLogs"
            }
        ],
        "failed_checks": [
            {
                "check_id": "CKV_AWS_21",
                "check_name": "Ensure all data stored in the S3 bucket have versioning enabled",
                "check_result": {
                    "result": "FAILED"
                },
                "code_block": [
                    [
                        1,
                        "resource \"aws_s3_bucket\" \"foo-bucket\" {\n"
                    ],
                    [
                        2,
                        "  region        = var.region\n"
                    ],
                    [
                        3,
                        "  bucket        = local.bucket_name\n"
                    ],
                    [
                        4,
                        "  force_destroy = true\n"
                    ],
                    [
                        5,
                        "  #checkov:skip=CKV_AWS_20:The bucket is a public static content host\n"
                    ],
                    [
                        6,
                        "  tags = {\n"
                    ],
                    [
                        7,
                        "    Name = \"foo-${data.aws_caller_identity.current.account_id}\"\n"
                    ],
                    [
                        8,
                        "  }\n"
                    ],
                    [
                        9,
                        "  versioning {\n"
                    ],
                    [
                        10,
                        "    enabled = false\n"
                    ],
                    [
                        11,
                        "  }\n"
                    ],
                    [
                        12,
                        "  logging {\n"
                    ],
                    [
                        13,
                        "    target_bucket = \"${aws_s3_bucket.log_bucket.id}\"\n"
                    ],
                    [
                        14,
                        "    target_prefix = \"log/\"\n"
                    ],
                    [
                        15,
                        "  }\n"
                    ],
                    [
                        16,
                        "  server_side_encryption_configuration {\n"
                    ],
                    [
                        17,
                        "    rule {\n"
                    ],
                    [
                        18,
                        "      apply_server_side_encryption_by_default {\n"
                    ],
                    [
                        19,
                        "        kms_master_key_id = \"${aws_kms_key.mykey.arn}\"\n"
                    ],
                    [
                        20,
                        "        sse_algorithm     = \"aws:kms\"\n"
                    ],
                    [
                        21,
                        "      }\n"
                    ],
                    [
                        22,
                        "    }\n"
                    ],
                    [
                        23,
                        "  }\n"
                    ],
                    [
                        24,
                        "  acl           = \"public-read\"\n"
                    ],
                    [
                        25,
                        "}\n"
                    ]
                ],
                "file_path": "/example.tf",
                "file_line_range": [
                    1,
                    25
                ],
                "resource": "aws_s3_bucket.foo-bucket",
                "check_class": "checkov.terraform.checks.resource.aws.S3Versioning"
            }
        ],
        "skipped_checks": [
            {
                "check_id": "CKV_AWS_20",
                "check_name": "S3 Bucket has an ACL defined which allows public access.",
                "check_result": {
                    "result": "SKIPPED",
                    "suppress_comment": "The bucket is a public static content host"
                },
                "code_block": [
                    [
                        1,
                        "resource \"aws_s3_bucket\" \"foo-bucket\" {\n"
                    ],
                    [
                        2,
                        "  region        = var.region\n"
                    ],
                    [
                        3,
                        "  bucket        = local.bucket_name\n"
                    ],
                    [
                        4,
                        "  force_destroy = true\n"
                    ],
                    [
                        5,
                        "  #checkov:skip=CKV_AWS_20:The bucket is a public static content host\n"
                    ],
                    [
                        6,
                        "  tags = {\n"
                    ],
                    [
                        7,
                        "    Name = \"foo-${data.aws_caller_identity.current.account_id}\"\n"
                    ],
                    [
                        8,
                        "  }\n"
                    ],
                    [
                        9,
                        "  versioning {\n"
                    ],
                    [
                        10,
                        "    enabled = false\n"
                    ],
                    [
                        11,
                        "  }\n"
                    ],
                    [
                        12,
                        "  logging {\n"
                    ],
                    [
                        13,
                        "    target_bucket = \"${aws_s3_bucket.log_bucket.id}\"\n"
                    ],
                    [
                        14,
                        "    target_prefix = \"log/\"\n"
                    ],
                    [
                        15,
                        "  }\n"
                    ],
                    [
                        16,
                        "  server_side_encryption_configuration {\n"
                    ],
                    [
                        17,
                        "    rule {\n"
                    ],
                    [
                        18,
                        "      apply_server_side_encryption_by_default {\n"
                    ],
                    [
                        19,
                        "        kms_master_key_id = \"${aws_kms_key.mykey.arn}\"\n"
                    ],
                    [
                        20,
                        "        sse_algorithm     = \"aws:kms\"\n"
                    ],
                    [
                        21,
                        "      }\n"
                    ],
                    [
                        22,
                        "    }\n"
                    ],
                    [
                        23,
                        "  }\n"
                    ],
                    [
                        24,
                        "  acl           = \"public-read\"\n"
                    ],
                    [
                        25,
                        "}\n"
                    ]
                ],
                "file_path": "/example.tf",
                "file_line_range": [
                    1,
                    25
                ],
                "resource": "aws_s3_bucket.foo-bucket",
                "check_class": "checkov.terraform.checks.resource.aws.S3PublicACL"
            }
        ],
        "parsing_errors": []
    },
    "summary": {
        "passed": 2,
        "failed": 1,
        "skipped": 1,
        "parsing_errors": 0,
        "checkov_version": "1.0.63"
    }
}
```

### Sample policy

Each Checkov policy is defined by resources it scans and expected values for related resource blocks.

For example, a policy that ensures all data is stored in S3 is versioned, scans the ``versioning`` configuration for all ``aws_s3_bucket`` supported resources. The `scan_resource_conf` is a method that defines the scan's expected behavior, i.e. ``versioning_block['enabled']``

```python
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
class S3Versioning(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket is versioned"
        id = "CKV_AWS_21"
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

Consider the following Terraform AWS S3 bucket configuration:
```
# example_versioning_pass.tf
resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true

  tags = {
    Name = "foo-${data.aws_caller_identity.current.account_id}"
  }
  versioning {
    enabled = true
  }

```

Running `checkov -d ./example_versioning_pass.tf -o cli` would yield a `PASSED` check result for the `S3Versioning` scanner:

```bash
...
Check: "Ensure all data stored in the S3 bucket have versioning enabled"
	PASSED for resource: aws_s3_bucket.foo-bucket
	File: /example.tf:1-24
...
```

If the scanned configuration would have been without bucket versioning enabled, the corresponding check would fail:

Configuration:

```bash
example_acl_fail.tf
resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true

  tags = {
    Name = "foo-${data.aws_caller_identity.current.account_id}"
  }
  versioning {
    enabled = false
  }
}

```
Run result:


```bash
> checkov -d ./example_versioning_fail.tf -o cli

Check: "Ensure all data stored in the S3 bucket have versioning enabled"
	FAILED for resource: aws_s3_bucket.foo-bucket
	File: /example_versioning_fail.tf:1-12

		1 | resource "aws_s3_bucket" "foo-bucket" {
		2 |   region        = var.region
		3 |   bucket        = local.bucket_name
		4 |   force_destroy = true
		5 |
		6 |   tags = {
		7 |     Name = "foo-${data.aws_caller_identity.current.account_id}"
		8 |   }
		9 |   versioning {
		10 |     enabled = false
		11 |   }
		12 | }
```

## What's Next?
From this point, you can head to the [Policies](Policies.md) for further examples or the How-to Guides section if you’re ready to get your hands dirty.
