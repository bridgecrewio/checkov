---
layout: default
published: true
title: Evaluations
order: 7
---
# Evaluations

Checkov supports the evaluation of variables, found in Terraform expressions.
Variables are declared in `.tf` files, where each variable has an identifying name,
a description, and an optional default value.

Checkov collects the default values of variables and assigns them
to their corresponding references in Terraform expressions.

The advantage of variable evaluation is to cover optional scenarios, in which a forbidden value of a
variable, is set inside a Terraform resource configuration. In that scenario, the resource
would maybe not meet with certain security compliance.

# Example

Recall the `CKV_AWS_20` check, which validates if an S3 Bucket has an ACL defined which allows
public access:
```python
class S3PublicACL(BaseResourceCheck):
    def __init__(self):
        name = "S3 Bucket has an ACL defined which allows public access."
        id = "CKV_AWS_20"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for ACL configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'acl' in conf.keys():
            acl_block = conf['acl']
            if acl_block in [["public-read"],["public-read-write"],["website"]]:
                return CheckResult.FAILED
        return CheckResult.PASSED

```
Suppose the following Terraform configuration:

```terraform
# ./main.tf
resource "aws_s3_bucket" "my_bucket" {
  region        = var.region
  bucket        = local.bucket_name
  acl           = var.acl
  force_destroy = true
}

```
and the following variable file:

```terraform
# ./variables.tf

variable "bucket_name" {
  default = "MyBucket"
}

variable "acl" {
  default = "public-read"
}

variable "region" {
  default = "us-west-2"
}

```
Checkov would evaluate `var.acl` variable to `public-acl`, resulting the check to fail:

```bash
> checkov -d .
...
Check: CKV_AWS_20: "S3 Bucket has an ACL defined which allows public access."
	FAILED for resource: aws_s3_bucket.my_bucket
	File: /main.tf:24-29

		24 | resource "aws_s3_bucket" "my_bucket" {
		25 |   region        = var.region
		26 |   bucket        = local.bucket_name
		27 |   acl           = var.acl
		28 |   force_destroy = true
		29 | }
	Variable acl evaluated to value public-read in expression: acl = ${var.acl}
	Variable region evaluated to value us-west-2 in expression: region = ${var.region}
```
To make the check pass, the value of `var.acl` needs to be set to `private` as follows:

```terraform
# ./variables.tf
...
variable "acl" {
  default = "private"
}
```

The check result would then pass:
```bash
Check: CKV_AWS_20: "S3 Bucket has an ACL defined which allows public access."
	PASSED for resource: aws_s3_bucket.template_bucket
	File: /main.tf:24-29

	Variable acl evaluated to value private in expression: acl = ${var.acl}
	Variable region evaluated to value us-west-2 in expression: region = ${var.region}
```