---
layout: default
published: true
title: OpenAI
nav_order: 20
---

# OpenAI

It is possible to use OpenAI ChatGPT functionality to enhance checkov's findings by setting the flag `--openai-api-key`.

ex.
```shell
checkov -d . --openai-api-key sk-...

       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: 3.0.1

WARNING: About to request 5 enhanced guidelines and it may take up to 15s.
Found 100 failed checks and will provide enhanced guidelines for 5. To add enhanced guidelines for more findings,
please adjust the env var 'CKV_OPENAI_MAX_FINDINGS' accordingly or set 0 to enhance all.

terraform scan results:
Check: CKV_AWS_211: "Ensure RDS uses a modern CaCert"
	PASSED for resource: aws_db_instance.pass
	Severity: LOW
	File: /main.tf:25-38
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-aws-rds-uses-a-modern-cacert
Check: CKV_AWS_16: "Ensure all data stored in the RDS is securely encrypted at rest"
	FAILED for resource: aws_db_instance.pass
	Severity: MEDIUM
	Details: The following text is AI generated and should be treated as a suggestion.
	         
	         The given code creates an AWS RDS instance with MySQL engine version 5.7, with a 10GB allocated storage, and a retention period of 7 days.
	         However, it does not specify any encryption settings for the RDS instance, which violates the checkov policy 'Ensure all data stored in the RDS is securely encrypted at rest'.
	         This means that sensitive data stored in the RDS instance may be vulnerable to unauthorized access or theft.
	         
	         To fix this, we need to enable encryption for the RDS instance.
	         AWS RDS provides two options for encryption: AWS managed encryption and customer-managed encryption.
	         In this case, we will use AWS managed encryption, which is the simpler option.
	         
	         To enable AWS managed encryption, we need to add the following block to the resource definition:
	         
	           storage_encrypted = true
	           kms_key_id        = "alias/aws/rds"
	         
	         The `storage_encrypted` parameter enables encryption for the RDS instance, and the `kms_key_id` parameter specifies the AWS KMS key to use for encryption.
	         In this case, we are using the default AWS RDS KMS key.
	         
	         The updated code with encryption enabled will look like this:
	         
	         resource "aws_db_instance" "pass" {
	           allocated_storage      = 10
	           db_name                = "mydb"
	           engine                 = "mysql"
	           engine_version         = "5.7"
	           instance_class         = "db.t3.micro"
	           username               = "foo"
	           password               = "foobarbaz"
	           parameter_group_name   = "default.mysql5.7"
	           skip_final_snapshot    = true
	           copy_tags_to_snapshot  = true
	           backup_retention_period = 7
	         
	           storage_encrypted = true
	           kms_key_id        = "alias/aws/rds"
	         }
	         
	         With this change, the RDS instance will be encrypted at rest, and will comply with the checkov policy.
	File: /main.tf:25-38
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-4

		25 | resource "aws_db_instance" "pass" {
		26 |   allocated_storage    = 10
		27 |   db_name              = "mydb"
		28 |   engine               = "mysql"
		29 |   engine_version       = "5.7"
		30 |   instance_class       = "db.t3.micro"
		31 |   username             = "foo"
		32 |   password             = "foobarbaz"
		33 |   parameter_group_name = "default.mysql5.7"
		34 |   skip_final_snapshot  = true
		35 |   copy_tags_to_snapshot = true
		36 | 
		37 |   backup_retention_period = 7
		38 | }


Passed checks: 1, Failed checks: 1, Skipped checks: 0
```

## Settings

Following environment variables can be used to fine tune the amount of AI generated guidelines.

| Environment variable    | Default       | Info                                                         |
|-------------------------|---------------|--------------------------------------------------------------|
| CKV_OPENAI_API_KEY      |               | OpenAI API key instead of using the flag.                    |
| CKV_OPENAI_MAX_FINDINGS | 5             | Amount of findings per framework to add enhanced guidelines. |
| CKV_OPENAI_MAX_TOKENS   | 512           | Maximum number of tokens to generate in the chat completion. |
| CKV_OPENAI_MODEL        | gpt-3.5-turbo | ID of the chat completion model to use.                      |
