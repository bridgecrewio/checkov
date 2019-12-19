---
layout: default
published: true
title: Results
order: 4
---

# Results

## Scan outputs

After running a ``checkov`` command on a Terraform file or folder, the scan's results will print in your current session Checkov currently supports output in 3 common formats: CLI, JSON & JUnit XML. 



### CLI Output

Running a Checkov scan with no output parameter will result in a color-coded CLI print output.

```
checkov -d /user/tf
```

Each print includes a scan summary and detailed scan results following.

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
		84 |   acl           = "public-read"
		85 |   # checkov:skip=CKV_AWS_20: The bucket is a public static content host
		86 |   acl           = "public-read"
		87 |   force_destroy = true
		88 |    # checkov:skip=CKV_AWS_19: Bucket access logs is not required for public content
		89 |   tags = {
		90 |     Name = "${local.bucket_name}-${data.aws_caller_identity.current.account_id}"
		91 |   }
		92 | }

Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
	SKIPPED for resource: aws_s3_bucket.template_bucket
	Suppress comment: The bucket is a public static content host, that does not require encryption
	File: /main.tf:81-92     ```
```

### JSON Output

Running a Checkov scan with the JSON output parameter (```-o json```) will result in JSON print output.

```
checkov -d /user/tf -o json
```

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
The print includes detailed structured data-blocks that contain exact references to code blocks, line ranges, optional skipped checks,
and scanned resources.



### JUnit XML

Running a Checkov scan with the JSON output parmeter (```-o junitxml```) will result in JUnit XML print output.

```
checkov -d /user/tf -o junitxml
```

This print also includes detailed structured data-blocks that contain exact references to code blocks, line ranges and resources scanned.

```xml
<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="1" tests="4" time="0.0">
	<testsuite disabled="0" errors="0" failures="0" name="Ensure all data stored in the S3 bucket is securely encrypted at rest" package="checkov.terraform.checks.resource.aws.S3Encryption" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3Encryption" file="/example.tf" name="Ensure all data stored in the S3 bucket is securely encrypted at rest aws_s3_bucket.foo-bucket"/>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="0" name="Ensure the S3 bucket has access logging enabled" package="checkov.terraform.checks.resource.aws.S3AccessLogs" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3AccessLogs" file="/example.tf" name="Ensure the S3 bucket has access logging enabled aws_s3_bucket.foo-bucket"/>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="1" name="Ensure all data stored in the S3 bucket have versioning enabled" package="checkov.terraform.checks.resource.aws.S3Versioning" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3Versioning" file="/example.tf" name="Ensure all data stored in the S3 bucket have versioning enabled aws_s3_bucket.foo-bucket">
			<failure message="Resource &quot;aws_s3_bucket.foo-bucket&quot; failed in check &quot;Ensure all data stored in the S3 bucket have versioning enabled&quot;" type="failure"/>
		</testcase>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="0" name="S3 Bucket has an ACL defined which allows public access." package="checkov.terraform.checks.resource.aws.S3PublicACL" skipped="1" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3PublicACL" file="/example.tf" name="S3 Bucket has an ACL defined which allows public access. aws_s3_bucket.foo-bucket">
			<skipped message="Resource &quot;aws_s3_bucket.foo-bucket&quot; skipped in check &quot;S3 Bucket has an ACL defined which allows public access.&quot;
 Suppress comment: The bucket is a public static content host" type="skipped"/>
		</testcase>
	</testsuite>
</testsuites>
```

## Next Steps

Explore the [suppression](../2.Concepts/Suppressions.md)

