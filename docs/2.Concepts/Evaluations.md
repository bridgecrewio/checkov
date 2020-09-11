---
layout: default
published: true
title: Variable Evaluation
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

## Example

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

### CLI output
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
	Variable acl (of /variables.tf) evaluated to value "public-acl" in expression: acl = ${var.acl}
	Variable region (of /variables.tf) evaluated to value "us-west-2" in expression: region = ${var.region}
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

	Variable acl (of /variables.tf) evaluated to value "public-acl" in expression: acl = ${var.acl}
	Variable region (of /variables.tf) evaluated to value "us-west-2" in expression: region = ${var.region}
```

### JSON Output
If available, each `PASSED/FAILED` check contains the evaluation information, which contains all the variables
 who were evaluated.

Each variable contains it's variable source file path, the evaluated value and the expressions in
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

# Further Terraform Concepts

## Scanning third party Terraform modules

Third party Terraform modules often reduce complexity for deploying services made up of many objects.

For example, the third party EKS module by howdio reduces the terraform required to the nine lines below, however, in doing so abstracts the terraform configuration away from a regular Checkov scan on the current directory.

```
module "eks" {
  source = "howdio/eks/aws"

  name        = "examplecluster"
  default_vpc = true

  enable_kubectl   = true
  enable_dashboard = true
}
```

To ensure coverage of objects within these modules, you can instruct checkov to scan the `.terraform` directory, after a `terraform init`, which will have retrieved the third party modules and any associated `.tf` files.

```sh
terraform init
checkov -d . # Your TF files.
checkov -d .terraform # Module TF files.
```


![module-scanning-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/scanning-terraform-module.png)


It is worth noting however, when scanning the `.terraform` directory, Checkov cannot differentiate between third party and internally written modules, however, you will gain scanning coverage for all of them.
