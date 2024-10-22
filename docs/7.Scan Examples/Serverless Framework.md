---
layout: default
published: true
title: Serverless framework configuration scanning
nav_order: 20
---

# Serverless framework configuration scanning
Checkov supports the evaluation of policies on your Serverless framework files.
When using checkov to scan a directory that contains a Serverless framework template it will validate if the file is compliant with AWS best practices such as having logging and auditing enabled, making sure S3 buckets are encrypted, HTTPS is being used, and more.  

Full list of Serverless framework policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/serverless.html).
The serverless scanning is utilizing checks that are part of the Cloudformation scanning implementation of checkov since Serverless resource definition extends the Cloudformation definition.  

### Example misconfigured Serverless framework

```yaml
service: usersCrud
provider: aws

functions:
  myFunc:
    name: myFunc
    tags:
      RESOURCE: lambda
      PUBLIC: false
    iamRoleStatements:
      - Effect: Allow
        Action:
          - "lambda:InvokeFunction"
        Resource:
          - "arn:aws:lambda:#{AWS::Region}:#{AWS::AccountId}:function:invokedLambda"
    handler: Handler.handle
    timeout: 600
    memorySize: 320

resources: # CloudFormation template syntax
  Resources:
    S3BucketPublicRead:
      Type: AWS::S3::Bucket
      Properties:
        AccessControl: PublicRead
        BucketEncryption:
          ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SSEAlgorithm: AES256

```
### Running in CLI

```bash
checkov -d . --framework serverless
```

### Example output

```bash

       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x 


serverless scan results:

Passed checks: 5, Failed checks: 7, Skipped checks: 0

Check: CKV_AWS_19: "Ensure the S3 bucket has server-side-encryption enabled"
   PASSED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-14-data-encrypted-at-rest

Check: CKV_AWS_57: "Ensure the S3 bucket does not allow WRITE permissions to everyone"
   PASSED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-2-acl-write-permissions-everyone

Check: CKV_AWS_49: "Ensure no IAM policies documents allow "*" as a statement's actions"
   PASSED for resource: myFunc
   File:/serverless.yml:5-19
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/bc_aws_iam_43

Check: CKV_AWS_41: "Ensure no hard coded AWS access key and secret key exists in provider"
   PASSED for resource: myFunc
   File:/serverless.yml:5-19
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/bc_aws_secrets_5

Check: CKV_AWS_1: "Ensure IAM policies that allow full "*-*" administrative privileges are not created"
   PASSED for resource: myFunc
   File:/serverless.yml:5-19
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/iam_23

Check: CKV_AWS_20: "Ensure the S3 bucket does not allow READ permissions to everyone"
   FAILED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_1-acl-read-permissions-everyone

      22 |     S3BucketPublicRead:
      23 |       Type: AWS::S3::Bucket
      24 |       Properties:
      25 |         AccessControl: PublicRead
      26 |         BucketEncryption:
      27 |           ServerSideEncryptionConfiguration:
      28 |             - ServerSideEncryptionByDefault:
      29 |                 SSEAlgorithm: AES256

Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
   FAILED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_13-enable-logging

      22 |     S3BucketPublicRead:
      23 |       Type: AWS::S3::Bucket
      24 |       Properties:
      25 |         AccessControl: PublicRead
      26 |         BucketEncryption:
      27 |           ServerSideEncryptionConfiguration:
      28 |             - ServerSideEncryptionByDefault:
      29 |                 SSEAlgorithm: AES256

Check: CKV_AWS_53: "Ensure S3 bucket has block public ACLS enabled"
   FAILED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/bc_aws_s3_19

      22 |     S3BucketPublicRead:
      23 |       Type: AWS::S3::Bucket
      24 |       Properties:
      25 |         AccessControl: PublicRead
      26 |         BucketEncryption:
      27 |           ServerSideEncryptionConfiguration:
      28 |             - ServerSideEncryptionByDefault:
      29 |                 SSEAlgorithm: AES256

Check: CKV_AWS_54: "Ensure S3 bucket has block public policy enabled"
   FAILED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/bc_aws_s3_20

      22 |     S3BucketPublicRead:
      23 |       Type: AWS::S3::Bucket
      24 |       Properties:
      25 |         AccessControl: PublicRead
      26 |         BucketEncryption:
      27 |           ServerSideEncryptionConfiguration:
      28 |             - ServerSideEncryptionByDefault:
      29 |                 SSEAlgorithm: AES256

Check: CKV_AWS_21: "Ensure the S3 bucket has versioning enabled"
   FAILED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_16-enable-versioning

      22 |     S3BucketPublicRead:
      23 |       Type: AWS::S3::Bucket
      24 |       Properties:
      25 |         AccessControl: PublicRead
      26 |         BucketEncryption:
      27 |           ServerSideEncryptionConfiguration:
      28 |             - ServerSideEncryptionByDefault:
      29 |                 SSEAlgorithm: AES256

Check: CKV_AWS_55: "Ensure S3 bucket has ignore public ACLs enabled"
   FAILED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/bc_aws_s3_21

      22 |     S3BucketPublicRead:
      23 |       Type: AWS::S3::Bucket
      24 |       Properties:
      25 |         AccessControl: PublicRead
      26 |         BucketEncryption:
      27 |           ServerSideEncryptionConfiguration:
      28 |             - ServerSideEncryptionByDefault:
      29 |                 SSEAlgorithm: AES256

Check: CKV_AWS_56: "Ensure S3 bucket has 'restrict_public_bucket' enabled"
   FAILED for resource: AWS::S3::Bucket.S3BucketPublicRead
   File:/serverless.yml:22-29
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/bc_aws_s3_22

      22 |     S3BucketPublicRead:
      23 |       Type: AWS::S3::Bucket
      24 |       Properties:
      25 |         AccessControl: PublicRead
      26 |         BucketEncryption:
      27 |           ServerSideEncryptionConfiguration:
      28 |             - ServerSideEncryptionByDefault:
      29 |                 SSEAlgorithm: AES256


```
