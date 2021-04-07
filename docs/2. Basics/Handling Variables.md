---
layout: default
published: true
title: Handling Variables
order: 8
---
# Evaluations

Checkov supports the evaluation of variables found in Terraform expressions.
Variables are declared in `.tf` files, where each variable has an identifying name, a description, and an optional default value.
Checkov collects the default values of variables and assigns them to their corresponding references in Terraform expressions.
The advantage of variable evaluation is to cover optional scenarios, in which a forbidden value of a variable is set inside a Terraform resource configuration. In that scenario, the resource may not comply to security standards. 

## Example

This example uses the `CKV_AWS_20` check, which validates if an S3 Bucket has an ACL defined which allows public access:
[block:code]
{
  "codes": [
    {
      "code": "class S3PublicACL(BaseResourceCheck):\n    def __init__(self):\n        name = \"S3 Bucket has an ACL defined which allows public access.\"\n        id = \"CKV_AWS_20\"\n        supported_resources = ['aws_s3_bucket']\n        categories = [CheckCategories.GENERAL_SECURITY]\n        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)\n\n    def scan_resource_conf(self, conf):\n        \"\"\"\n            Looks for ACL configuration at aws_s3_bucket:\n            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html\n        :param conf: aws_s3_bucket configuration\n        :return: <CheckResult>\n        \"\"\"\n        if 'acl' in conf.keys():\n            acl_block = conf['acl']\n            if acl_block in [[\"public-read\"],[\"public-read-write\"],[\"website\"]]:\n                return CheckResult.FAILED\n        return CheckResult.PASSED",
      "language": "python",
      "name": " "
    }
  ]
}
[/block]
If we have the Terraform configuration and variable files below, Checkov evaluates the `var.acl` variable to `public-acl`, which results in the check failing:
[block:code]
{
  "codes": [
    {
      "code": "# ./main.tf\nresource \"aws_s3_bucket\" \"my_bucket\" {\n  region        = var.region\n  bucket        = local.bucket_name\n  acl           = var.acl\n  force_destroy = true\n}",
      "language": "python",
      "name": "Terraform Configuration File"
    }
  ]
}
[/block]

[block:code]
{
  "codes": [
    {
      "code": "# ./variables.tf\n\nvariable \"bucket_name\" {\n  default = \"MyBucket\"\n}\n\nvariable \"acl\" {\n  default = \"public-read\"\n}\n\nvariable \"region\" {\n  default = \"us-west-2\"\n}\n\n### CLI output",
      "language": "python",
      "name": "Variable File"
    }
  ]
}
[/block]

[block:code]
{
  "codes": [
    {
      "code": "> checkov -d .\n...\nCheck: CKV_AWS_20: \"S3 Bucket has an ACL defined which allows public access.\"\n\tFAILED for resource: aws_s3_bucket.my_bucket\n\tFile: /main.tf:24-29\n\n\t\t24 | resource \"aws_s3_bucket\" \"my_bucket\" {\n\t\t25 |   region        = var.region\n\t\t26 |   bucket        = local.bucket_name\n\t\t27 |   acl           = var.acl\n\t\t28 |   force_destroy = true\n\t\t29 | }\n\tVariable acl (of /variables.tf) evaluated to value \"public-acl\" in expression: acl = ${var.acl}\n\tVariable region (of /variables.tf) evaluated to value \"us-west-2\" in expression: region = ${var.region}",
      "language": "python",
      "name": "Failed Check"
    }
  ]
}
[/block]
To pass the check, the value of `var.acl` needs to be set to `private` as follows:
[block:code]
{
  "codes": [
    {
      "code": "# ./variables.tf\n...\nvariable \"acl\" {\n  default = \"private\"\n}",
      "language": "python"
    }
  ]
}
[/block]
The check result now passes:
[block:code]
{
  "codes": [
    {
      "code": "Check: CKV_AWS_20: \"S3 Bucket has an ACL defined which allows public access.\"\n\tPASSED for resource: aws_s3_bucket.template_bucket\n\tFile: /main.tf:24-29\n\n\tVariable acl (of /variables.tf) evaluated to value \"public-acl\" in expression: acl = ${var.acl}\n\tVariable region (of /variables.tf) evaluated to value \"us-west-2\" in expression: region = ${var.region}",
      "language": "python"
    }
  ]
}
[/block]
### JSON Output
If available, each `PASSED/FAILED` check contains the evaluation information, which contains all the variables that were evaluated.
Each variable contains its variable source file path, the evaluated value, and the expressions in
which it was referenced:
[block:code]
{
  "codes": [
    {
      "code": "evaluations: {\n  '<var_name>': {\n    'var_file': '<variable_file_relative_path>',\n    'value': '<value>',\n    'definitions': [\n      {\n        'definition_name': 'name',\n        'definition_expression': '${var.customer_name}_group',\n        'definition_path': 'resource/0/aws_cognito_user_group/user_group/name/0'\n      },\n      {\n        'definition_name': 'description',\n        'definition_expression': '${var.customer_name} user group',\n        'definition_path': 'resource/0/aws_cognito_user_group/user_group/description/0'\n      }\n    ]\n  },\n  ...\n}",
      "language": "json"
    }
  ]
}
[/block]