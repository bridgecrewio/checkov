---
layout: default
published: true
title: Scanning Credentials and Secrets
nav_order: 5
---

# Scanning Credentials and Secrets

Checkov can scan for a number of different common credentials such as AWS access keys, Azure service credentials, or private keys that are hard-coded in a Terraform code block.
See list of regular expressions [here](https://github.com/bridgecrewio/checkov/blob/main/checkov/common/util/secrets.py).

Let’s assume we have the following Terraform provider block:

```yaml
# Snippet from  main.tf
provider "aws" {
  region     = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

As stated in Terraform's documentation: “Hard-coding credentials into any Terraform configuration is not recommended, and risks secret leakage should this file ever be committed to a public version control system.”

Run Checkov to detect secrets:

```shell
checkov -f main.tf
```

This is the output of the scan

```text
      _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
version: 1.0.202 

terraform scan results:

Passed checks: 0, Failed checks: 1, Skipped checks: 0

Check: CKV_AWS_41: "Ensure no hard coded AWS access key and secret key exists"
	FAILED for resource: provider.aws
	File: :1-5

		1 | provider "aws" {
		2 |   region     = "us-west-2"
		3 |   access_key = "AKIAIOSFODNN7EXAMPLE"
		4 |   secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
		5 | }
```
Checkov can also detect secrets defined in lambda variables as shown in the example below.

```yaml
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

or in EC2 user data as shown in the example below:

```yaml
resource "aws_instance" "compute_host" {
  # ec2 have plain text secrets in user data
  ami           = "ami-04169656fea786776"
  instance_type = "t2.nano"
  user_data     = <<EOF
#! /bin/bash
sudo apt-get update
sudo apt-get install -y apache2
sudo systemctl start apache2
sudo systemctl enable apache2
export AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-west-2
echo "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html
EOF
  tags = {
    Name  = "${local.resource_prefix.value}-ec2"
  }
}
```
