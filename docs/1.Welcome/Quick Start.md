---
layout: default
published: true
title: Quick Start
nav_order: 3
---

# Quick Start

This Quick Start guide shows how to install Checkov, run a scan, and analyze the results.
For more advanced configuration, see the [CLI Reference](https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html) and the rest of this documentation.

## Install Checkov from PyPI

```text
pip install checkov
```

## Select input folder and scan

Use the command below to indicate the folder that contains your Terraform plan files and run a scan.

```text
checkov -d /user/tf
```

## Example

### S3 Bucket configuration (compliant)

Consider the configuration of an S3 bucket as represented in the Terraform sample below.

```yaml
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

### Scan output for compliant S3 Bucket configuration

The scan output would be:

```xml
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

The configuration complies with the policies for AWS S3 resources.

### S3 Bucket configuration (non-compliant)

Suppose that now the same bucket is configured to allow public access:

```text
resource "aws_s3_bucket" "foo-bucket" {
#same resource configuration as previous example, but acl set for public access.
  
  acl           = "public-read"
}
data "aws_caller_identity" "current" {}
```

### Scan output for non-compliant S3 Bucket Configuration

The output report would then contain a failed check:

```xml
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

## Visualizing scan output

In addition to the various formats for seeing scan results (for example, CLI), you can also visualize Checkov results with a quick integration with a Prisma Cloud account. Read more about [visualizing scan results in Prisma Cloud](https://www.checkov.io/2.Basics/Visualizing%20Checkov%20Output.html).

## Integrations

In addition to integrating with your code repository, Checkov can also integrate with your automated build pipeline via CI/CD providers. When your build tests run, Checkov will scan your infrastructure as code files for misconfigurations.
You can integrate Checkov with:

* [Jenkins](https://www.checkov.io/4.Integrations/Jenkins.html)
* [Bitbucket Cloud Pipelines](https://www.checkov.io/4.Integrations/Bitbucket%20Cloud%20Pipelines.html)
* [GitHub Actions](https://www.checkov.io/4.Integrations/GitHub%20Actions.html)
* [GitLab CI](https://www.checkov.io/4.Integrations/GitLab%20CI.html)
* [Kubernetes](https://www.checkov.io/4.Integrations/Kubernetes.html)
* [Pre-Commit](https://www.checkov.io/4.Integrations/pre-commit.html)
* [Docker](https://www.checkov.io/4.Integrations/Docker.html)
* [Terraform Plans and Third-Party Modules](https://www.checkov.io/7.Scan%20Examples/Terraform%20Plan%20Scanning.html)

## Add-ons

To get real-time IaC scanning and in-line fixes directly from your IDE, check out the [Checkov Visual Studio Code extension](https://marketplace.visualstudio.com/items?itemName=Bridgecrew.checkov) and the [Checkov JetBrains Plugin](https://plugins.jetbrains.com/plugin/21907-prisma-cloud).