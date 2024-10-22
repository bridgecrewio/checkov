---
layout: default
published: true
title: SARIF
nav_order: 20
---

# SARIF

SARIF (Static Analysis Results Interchange Format) is a standard format for the output of static analysis tools.
It can be used to show alerts in your GitHub repository as a part of the code scanning experience.

A typical output looks like this
```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Checkov",
          "version": "2.3.55",
          "informationUri": "https://www.checkov.io/",
          "rules": [
            {
              "id": "CKV_AWS_21",
              "name": "Ensure the S3 bucket has versioning enabled",
              "shortDescription": {
                "text": "Ensure the S3 bucket has versioning enabled"
              },
              "fullDescription": {
                "text": "Ensure the S3 bucket has versioning enabled"
              },
              "help": {
                "text": "Ensure the S3 bucket has versioning enabled\nResource: aws_s3_bucket.operations"
              },
              "helpUri": "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-16-enable-versioning",
              "defaultConfiguration": {
                "level": "error"
              },
              "properties": {"security-severity": 8.9}
            },
            {
              "id": "CKV_AWS_3",
              "name": "Ensure all data stored in the EBS is securely encrypted",
              "shortDescription": {
                "text": "Ensure all data stored in the EBS is securely encrypted"
              },
              "fullDescription": {
                "text": "Ensure all data stored in the EBS is securely encrypted"
              },
              "help": {
                "text": "Ensure all data stored in the EBS is securely encrypted\nResource: aws_ebs_volume.web_host_storage"
              },
              "helpUri": "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-7",
              "defaultConfiguration": {
                "level": "error"
              },
              "properties": {"security-severity": 6.9}
            }
          ],
          "organization": "prisma"
        }
      },
      "results": [
        {
          "ruleId": "CKV_AWS_21",
          "ruleIndex": 0,
          "level": "error",
          "attachments": [],
          "message": {
            "text": "Ensure the S3 bucket has versioning enabled"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "s3.tf"
                },
                "region": {
                  "startLine": 1,
                  "endLine": 3,
                  "snippet": {
                    "text": "resource aws_s3_bucket \"operations\" {\n  bucket = \"example\"\n}\n"
                  }
                }
              }
            }
          ]
        },
        {
          "ruleId": "CKV_AWS_3",
          "ruleIndex": 1,
          "level": "error",
          "attachments": [],
          "message": {
            "text": "Ensure all data stored in the EBS is securely encrypted"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "ec2.tf"
                },
                "region": {
                  "startLine": 5,
                  "endLine": 7,
                  "snippet": {
                    "text": "resource aws_ebs_volume \"web_host_storage\" {\n  availability_zone = \"us-west-2a\"\n}\n"
                  }
                }
              }
            }
          ]
        }
      ]
    }
  ]
},
```

The output can be created via the output flag

```shell
checkov -d . -o sarif
```
The tool.driver.name field can be customised using the --custom-tool-name flag



## Structure

Further information on the different elements and attributes can be found [here](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html).
