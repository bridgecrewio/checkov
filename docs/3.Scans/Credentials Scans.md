---
layout: default
published: true
title: Credentials scans
order: 7
---

# Credentials scans

Cloud account secrets are a priceless target for an attacker to utilize cloud resources, leak data or harm the application infrastructure. 

Checkov can scan for aws credentials (`access key` and `secret key`) that are hard coded in a terraform code block. 

## Example 
Let's assume we have the following terraform provider block:
```hcl-terraform
# Snippet from  main.tf
provider "aws" {
  region     = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```
As mentioned in terraform official docs [here](https://www.terraform.io/docs/providers/aws/index.html#static-credentials):
"Hard-coding credentials into any Terraform configuration is not recommended, and risks secret leakage should this file ever be committed to a public version control system."

Running checkov to detect secrets:

```bash
checkov -f main.tf
```

Will result in the following output:

```bash

       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
version: 1.0.202 

terraform scan results:

Passed checks: 0, Failed checks: 1, Skipped checks: 0

Check: CKV_AWS_41: "Ensure no hard coded AWS access key and and secret key exists"
	FAILED for resource: provider.aws
	File: :1-5

		1 | provider "aws" {
		2 |   region     = "us-west-2"
		3 |   access_key = "AKIAIOSFODNN7EXAMPLE"
		4 |   secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
		5 | }

```

checkov can also detect secrets defined in lambda variables like the following example:

```hcl-terraform

resource "aws_lambda_function" "test_lambda" {
  filename      = "resources/lambda_function_payload.zip"
  function_name = "${local.resource_prefix.value}-analysis"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  handler       = "exports.test"

  source_code_hash = "${filebase64sha256("resources/lambda_function_payload.zip")}"

  runtime = "nodejs12.x"

  environment {
    variables = {
      access_key = "AKIAIOSFODNN7EXAMPLE"
      secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
  }
}
```