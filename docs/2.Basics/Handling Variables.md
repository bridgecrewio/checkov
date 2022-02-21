---
layout: default
published: true
title: Handling Variables
nav_order: 8
---

# Handling Variables

Checkov supports the evaluation of variables found in Terraform expressions.
Variables are declared in `.tf` files where each variable has an identifying name, description, and optional default value.
Checkov collects the default values of variables and assigns them to their corresponding references in Terraform expressions.
The advantage of variable evaluation is to cover optional scenarios in which a forbidden value of a variable is set inside a Terraform resource configuration. In that scenario, the resource may not comply to security standards. 

## Example

This example uses the `CKV_AWS_20` check which validates if an S3 Bucket has an ACL defined which allows public access:

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

If we have the Terraform configuration and variable files below, Checkov evaluates the `var.acl` variable to `public-acl`, which results in the check failing:

```python
# ./main.tf
resource "aws_s3_bucket" "my_bucket" {
  region        = var.region
  bucket        = local.bucket_name
  acl           = var.acl
  force_destroy = true
}
```

```python
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

### CLI output
```

```python
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
	Variable acl (of /variables.tf) evaluated to value "public-acl" in expression: acl = ${var.acl}
	Variable region (of /variables.tf) evaluated to value "us-west-2" in expression: region = ${var.region}
```

To pass the check, the value of `var.acl` needs to be set to `private` as follows:

```python
# ./variables.tf
...
variable "acl" {
  default = "private"
}
```


The check result now passes:

```python
Check: CKV_AWS_20: "S3 Bucket has an ACL defined which allows public access."
	PASSED for resource: aws_s3_bucket.template_bucket
	File: /main.tf:24-29

	Variable acl (of /variables.tf) evaluated to value "private" in expression: acl = ${var.acl}
	Variable region (of /variables.tf) evaluated to value "us-west-2" in expression: region = ${var.region}
```

### JSON Output
If available, each `PASSED/FAILED` check contains the evaluation information, which contains all the variables that were evaluated.
Each variable contains its variable source file path, the evaluated value, and the expressions in
which it was referenced:

```json
evaluations: {
  '<var_name>': {
    'var_file': '<variable_file_relative_path>',
    'value': '<value>',
    'definitions': [
      {
        'definition_name': 'name',
        'definition_expression': '${var.customer_name}_group',
        'definition_path': 'resource/0/aws_cognito_user_group/user_group/name/0'
      },
      {
        'definition_name': 'description',
        'definition_expression': '${var.customer_name} user group',
        'definition_path': 'resource/0/aws_cognito_user_group/user_group/description/0'
      }
    ]
  },
  ...
}
```
