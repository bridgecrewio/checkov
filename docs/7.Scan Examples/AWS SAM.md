---
layout: default
published: true
title: AWS SAM configuration scanning
nav_order: 20
---

# AWS SAM framework configuration scanning
Checkov supports the evaluation of policies on your SAM templates files.
When using checkov to scan a directory that contains a SAM template it will validate if the file is compliant with AWS best practices such as having logging and auditing enabled, making sure S3 buckets are encrypted, HTTPS is being used, and more.  

Full list of SAM policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/serverless.html).
The SAM scanning is utilizing checks that are part of the Cloudformation scanning implementation of checkov since SAM resource definition extends the Cloudformation definition.  

### Example misconfigured SAM framework

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
​
Resources:
  Enabled:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      TracingEnabled: true
      CacheClusterEnabled: true
      AccessLogSetting:
        DestinationArn: 'arn:aws:logs:us-east-1:123456789:log-group:my-log-group'
​
  Default:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod


```
### Running in CLI

```bash
checkov -d . --framework cloudformation
```

### Example output

```bash

      _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x 


cloudformation scan results:

Passed checks: 3, Failed checks: 3, Skipped checks: 0

Check: CKV_AWS_120: "Ensure API Gateway caching is enabled"
	PASSED for resource: AWS::Serverless::Api.Enabled
	File: /sam.yaml:5-12

Check: CKV_AWS_73: "Ensure API Gateway has X-Ray Tracing enabled"
	PASSED for resource: AWS::Serverless::Api.Enabled
	File: /sam.yaml:5-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/logging-15

Check: CKV_AWS_76: "Ensure API Gateway has Access Logging enabled"
	PASSED for resource: AWS::Serverless::Api.Enabled
	File: /sam.yaml:5-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/logging-17

Check: CKV_AWS_120: "Ensure API Gateway caching is enabled"
	FAILED for resource: AWS::Serverless::Api.Default
	File: /sam.yaml:14-17

		14 |   Default:
		15 |     Type: AWS::Serverless::Api
		16 |     Properties:
		17 |       StageName: prod


Check: CKV_AWS_73: "Ensure API Gateway has X-Ray Tracing enabled"
	FAILED for resource: AWS::Serverless::Api.Default
	File: /sam.yaml:14-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/logging-15

		14 |   Default:
		15 |     Type: AWS::Serverless::Api
		16 |     Properties:
		17 |       StageName: prod


Check: CKV_AWS_76: "Ensure API Gateway has Access Logging enabled"
	FAILED for resource: AWS::Serverless::Api.Default
	File: /sam.yaml:14-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/logging-17

		14 |   Default:
		15 |     Type: AWS::Serverless::Api
		16 |     Properties:
		17 |       StageName: prod

```
