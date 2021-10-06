---
layout: default
published: true
title: Reviewing Scan Results
nav_order: 5
---

# Reviewing Scan Results

The results of Checkov scans can be viewed in CLI, JSON, JUnit XML, SARIF, or Markdown

> Note: For Markdown output, you need to use `github_failed_only` as the `--output` type

## Scan Result Sample (CLI)

Consider the following Terraform configuration of an S3 bucket:

```python
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

```python
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

The bucket's current configuration seems to comply with the available ``aws_s3_bucket`` resource type checks.

However, if the bucket is going to be used for static content hosting, it requires additional configuration to allow public access:

```python
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

After configuring the bucket to allow public access, the output report contains the failed check:

```python
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

The corresponding check now fails, and the report includes the appropriate failing configuration source code.

In order to skip the failed check, we annotate the bucket with a suppression comment (which needs to appear inside the resource scope):

```python
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

Checkov then skips the ``CKV_AWS_20`` check, and the output report is:

```python
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
## Visualize Checkov output
Read more about [sending your Checkov scan results to the Bridgecrew platform](https://www.checkov.io/2.Basics/Visualizing%20Checkov%20Output.html).
