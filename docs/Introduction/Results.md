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
	File: /main.tf:81-92     ```

### JSON Output

Running a Checkov scan with the JSON output parmeter (```-o json```) will result in JSON print output.

```
checkov -d /user/tf -o json
```

The print includes detailed structured data-blocks that contain exact references to code blocks, line ranges, optional skipped checks,
and sacnned resources.

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
                    [
                        25,
                        "  region        = var.region\n"
                    ],
                    [
                        26,
                        "  bucket        = local.sls_deployment_bucket_name\n"
                    ],
                    [
                        27,
                        "  force_destroy = true\n"
                    ],
                    [
                        28,
                        "  acl           = \"private\"\n"
                    ],
                    [
                        29,
                        "  tags = {\n"
                    ],
                    [
                        30,
                        "    Name = local.sls_deployment_bucket_name\n"
                    ],
                    [
                        31,
                        "  }\n"
                    ],
                    [
                        32,
                        "}\n"
                    ]
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

### JUnit XML

Running a Checkov scan with the JSON output parmeter (```-o junitxml```) will result in JUnit XML print output.

```
checkov -d /user/tf -o junitxml
```

This print also includes detailed structured data-blocks that contain exact references to code blocks, line ranges and resources scanned.

```xml
<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="15" tests="24" time="0.0">
	<testsuite disabled="0" errors="0" failures="0" name="S3 Bucket has an ACL defined which allows public access." package="checkov.terraform.checks.resource.aws.S3PublicACL" skipped="1" tests="4" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3PublicACL" file="/../regionStack/main.tf" name="S3 Bucket has an ACL defined which allows public access. aws_s3_bucket.sls_deployment_bucket_name"/>
		<testcase classname="checkov.terraform.checks.resource.aws.S3PublicACL" file="/../../api/infra/base/appSite/main.tf" name="S3 Bucket has an ACL defined which allows public access. aws_s3_bucket.app_bucket"/>
		<testcase classname="checkov.terraform.checks.resource.aws.S3PublicACL" file="/../../scanners/infra/base/main.tf" name="S3 Bucket has an ACL defined which allows public access. aws_s3_bucket.scanner_results"/>
		<testcase classname="checkov.terraform.checks.resource.aws.S3PublicACL" file="/main.tf" name="S3 Bucket has an ACL defined which allows public access. aws_s3_bucket.template_bucket">
			<skipped message="Resource &quot;aws_s3_bucket.template_bucket&quot; skipped in check &quot;S3 Bucket has an ACL defined which allows public access.&quot;
 Suppress comment: No comment provided" type="skipped"/>
		</testcase>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="0" name="Ensure no security groups allow ingress from 0.0.0.0:0 to port 22" package="checkov.terraform.checks.resource.aws.SecurityGroupUnrestrictedIngress22" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.SecurityGroupUnrestrictedIngress22" file="/../../scanners/infra/base/main.tf" name="Ensure no security groups allow ingress from 0.0.0.0:0 to port 22 aws_security_group.scanner_tasks_sg"/>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="0" name="Ensure no security groups allow ingress from 0.0.0.0:0 to port 3389" package="checkov.terraform.checks.resource.aws.SecurityGroupUnrestrictedIngress3389" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.SecurityGroupUnrestrictedIngress3389" file="/../../scanners/infra/base/main.tf" name="Ensure no security groups allow ingress from 0.0.0.0:0 to port 3389 aws_security_group.scanner_tasks_sg"/>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="2" name="Ensure all data stored in the S3 bucket is securely encrypted at rest" package="checkov.terraform.checks.resource.aws.S3Encryption" skipped="1" tests="4" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3Encryption" file="/../../scanners/infra/base/main.tf" name="Ensure all data stored in the S3 bucket is securely encrypted at rest aws_s3_bucket.scanner_results"/>
		<testcase classname="checkov.terraform.checks.resource.aws.S3Encryption" file="/../regionStack/main.tf" name="Ensure all data stored in the S3 bucket is securely encrypted at rest aws_s3_bucket.sls_deployment_bucket_name">
			<failure message="Resource &quot;aws_s3_bucket.sls_deployment_bucket_name&quot; failed in check &quot;Ensure all data stored in the S3 bucket is securely encrypted at rest&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3Encryption" file="/../../api/infra/base/appSite/main.tf" name="Ensure all data stored in the S3 bucket is securely encrypted at rest aws_s3_bucket.app_bucket">
			<failure message="Resource &quot;aws_s3_bucket.app_bucket&quot; failed in check &quot;Ensure all data stored in the S3 bucket is securely encrypted at rest&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3Encryption" file="/main.tf" name="Ensure all data stored in the S3 bucket is securely encrypted at rest aws_s3_bucket.template_bucket">
			<skipped message="Resource &quot;aws_s3_bucket.template_bucket&quot; skipped in check &quot;Ensure all data stored in the S3 bucket is securely encrypted at rest&quot;
 Suppress comment: Honestly dear, I don't give a damn" type="skipped"/>
		</testcase>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="0" name="Ensure rotation for customer created CMKs is enabled" package="checkov.terraform.checks.resource.aws.KMSRotation" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.KMSRotation" file="/../../scanners/infra/base/main.tf" name="Ensure rotation for customer created CMKs is enabled aws_kms_key.scanner_key"/>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="4" name="Ensure the S3 bucket has access logging enabled" package="checkov.terraform.checks.resource.aws.S3AccessLogs" skipped="0" tests="4" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3AccessLogs" file="/main.tf" name="Ensure the S3 bucket has access logging enabled aws_s3_bucket.template_bucket">
			<failure message="Resource &quot;aws_s3_bucket.template_bucket&quot; failed in check &quot;Ensure the S3 bucket has access logging enabled&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3AccessLogs" file="/../regionStack/main.tf" name="Ensure the S3 bucket has access logging enabled aws_s3_bucket.sls_deployment_bucket_name">
			<failure message="Resource &quot;aws_s3_bucket.sls_deployment_bucket_name&quot; failed in check &quot;Ensure the S3 bucket has access logging enabled&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3AccessLogs" file="/../../api/infra/base/appSite/main.tf" name="Ensure the S3 bucket has access logging enabled aws_s3_bucket.app_bucket">
			<failure message="Resource &quot;aws_s3_bucket.app_bucket&quot; failed in check &quot;Ensure the S3 bucket has access logging enabled&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3AccessLogs" file="/../../scanners/infra/base/main.tf" name="Ensure the S3 bucket has access logging enabled aws_s3_bucket.scanner_results">
			<failure message="Resource &quot;aws_s3_bucket.scanner_results&quot; failed in check &quot;Ensure the S3 bucket has access logging enabled&quot;" type="failure"/>
		</testcase>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="4" name="Ensure all data stored in the S3 bucket have versioning enabled" package="checkov.terraform.checks.resource.aws.S3Versioning" skipped="0" tests="4" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.S3Versioning" file="/main.tf" name="Ensure all data stored in the S3 bucket have versioning enabled aws_s3_bucket.template_bucket">
			<failure message="Resource &quot;aws_s3_bucket.template_bucket&quot; failed in check &quot;Ensure all data stored in the S3 bucket have versioning enabled&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3Versioning" file="/../regionStack/main.tf" name="Ensure all data stored in the S3 bucket have versioning enabled aws_s3_bucket.sls_deployment_bucket_name">
			<failure message="Resource &quot;aws_s3_bucket.sls_deployment_bucket_name&quot; failed in check &quot;Ensure all data stored in the S3 bucket have versioning enabled&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3Versioning" file="/../../api/infra/base/appSite/main.tf" name="Ensure all data stored in the S3 bucket have versioning enabled aws_s3_bucket.app_bucket">
			<failure message="Resource &quot;aws_s3_bucket.app_bucket&quot; failed in check &quot;Ensure all data stored in the S3 bucket have versioning enabled&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.S3Versioning" file="/../../scanners/infra/base/main.tf" name="Ensure all data stored in the S3 bucket have versioning enabled aws_s3_bucket.scanner_results">
			<failure message="Resource &quot;aws_s3_bucket.scanner_results&quot; failed in check &quot;Ensure all data stored in the S3 bucket have versioning enabled&quot;" type="failure"/>
		</testcase>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="3" name="Ensure all data stored in the SNS topic is encrypted" package="checkov.terraform.checks.resource.aws.SNSTopicEncryption" skipped="0" tests="3" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.SNSTopicEncryption" file="/../regionStack/../../monitor/infra/../../utils/terraform/sns/main.tf" name="Ensure all data stored in the SNS topic is encrypted aws_sns_topic.sns_topic">
			<failure message="Resource &quot;aws_sns_topic.sns_topic&quot; failed in check &quot;Ensure all data stored in the SNS topic is encrypted&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.SNSTopicEncryption" file="/../regionStack/../../utils/terraform/sns/main.tf" name="Ensure all data stored in the SNS topic is encrypted aws_sns_topic.sns_topic">
			<failure message="Resource &quot;aws_sns_topic.sns_topic&quot; failed in check &quot;Ensure all data stored in the SNS topic is encrypted&quot;" type="failure"/>
		</testcase>
		<testcase classname="checkov.terraform.checks.resource.aws.SNSTopicEncryption" file="/../../compliances/infra/base/./remediations/base/../../../../../utils/terraform/sns/main.tf" name="Ensure all data stored in the SNS topic is encrypted aws_sns_topic.sns_topic">
			<failure message="Resource &quot;aws_sns_topic.sns_topic&quot; failed in check &quot;Ensure all data stored in the SNS topic is encrypted&quot;" type="failure"/>
		</testcase>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="1" name="Ensure all data stored in the SQS queue  is encrypted" package="checkov.terraform.checks.resource.aws.SQSQueueEncryption" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.SQSQueueEncryption" file="/../../logArchive/infra/base/laceworkCloudwatch/main.tf" name="Ensure all data stored in the SQS queue  is encrypted aws_sqs_queue.lacework">
			<failure message="Resource &quot;aws_sqs_queue.lacework&quot; failed in check &quot;Ensure all data stored in the SQS queue  is encrypted&quot;" type="failure"/>
		</testcase>
	</testsuite>
	<testsuite disabled="0" errors="0" failures="1" name="Ensure every security groups rule has a description" package="checkov.terraform.checks.resource.aws.SecurityGroupRuleDescription" skipped="0" tests="1" time="0">
		<testcase classname="checkov.terraform.checks.resource.aws.SecurityGroupRuleDescription" file="/../../scanners/infra/base/main.tf" name="Ensure every security groups rule has a description aws_security_group.scanner_tasks_sg">
			<failure message="Resource &quot;aws_security_group.scanner_tasks_sg&quot; failed in check &quot;Ensure every security groups rule has a description&quot;" type="failure"/>
		</testcase>
	</testsuite>
</testsuites>
```



## Next Steps

Explore the [Integrations](**TODO)

