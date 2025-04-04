---
layout: default
published: true
title: AWS CDK configuration scanning
nav_order: 20
---

# AWS CDK configuration scanning
Checkov supports the evaluation of policies on your CDK files by synthesizing a Cloudformation template out of the CDK code.

Full list of Cloudformation policies the checks can be found [here](https://www.checkov.io/5.Policy%20Index/cloudformation.html).


### Example misconfigured AWS CDK code 
python CDK example
```python

from aws_cdk import (
    aws_s3,
    Stack,
)
from constructs import Construct

# End generated code block.

class BucketApp(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #
        # RESOURCES
        #

        pipeline_artifact_bucket = aws_s3.CfnBucket(
            self,
            "PipelineArtifactBucket",
            access_control="Private",
            bucket_encryption=aws_s3.CfnBucket.BucketEncryptionProperty(
                server_side_encryption_configuration=[
                    aws_s3.CfnBucket.ServerSideEncryptionRuleProperty(
                        server_side_encryption_by_default=aws_s3.CfnBucket.ServerSideEncryptionByDefaultProperty(
                            sse_algorithm="AES256"
                        )
                    )
                ]
            ),
            public_access_block_configuration=aws_s3.BlockPublicAccess.BLOCK_ALL
        )
        pipeline_artifact_bucket.cfn_options.metadata = {
          'checkov': {
            'skip': [
              {
                'id': 'CKV_AWS_18',
                'comment': 'No need to ensure the S3 bucket has access logging enabled'
              }
            ]
          }
        }

```
typescript CDK example
```typescript
const bucket = new aws_s3.Bucket(this, 'MyBucket', {
  versioned: true
});
const cfnBucket = bucket.node.defaultChild as aws_s3.CfnBucket;

cfnBucket.cfnOptions.metadata = {
  'checkov': {
    'skip': [
      {
        'id': 'CKV_AWS_18',
        'comment': 'No need to ensure the S3 bucket has access logging enabled'
      }
    ]
  }
}
```
The metadata secution contain 1 skip for CKV_AWS_18
Run the `cdk synth` command to generate a CloudFormation template and scan it
```json
{
  "Resources": {
    "MyBucketF68F3FF0": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "VersioningConfiguration": {
          "Status": "Enabled"
        }
      },
      "UpdateReplacePolicy": "Retain",
      "DeletionPolicy": "Retain",
      "Metadata": {
        "checkov": {
          "skip": [
            {
              "id": "CKV_AWS_18",
              "comment": "No need to ensure the S3 bucket has access logging enabled"
            }
          ]
        }
      }
    },
    "CDKMetadata": {
      "Type": "AWS::CDK::Metadata",
      "Properties": {
        "Analytics": "v2:deflate64:f"
      },
      "Metadata": {
        "aws:cdk:path": "AppStack/CDKMetadata/Default"
      },
      "Condition": "CDKMetadataAvailable"
    }
  },
  "Conditions": {
    "CDKMetadataAvailable": {
      "Fn::Or": [
        {
          "Fn::Or": [
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "af-south-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "ap-east-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "ap-northeast-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "ap-northeast-2"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "ap-south-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "ap-southeast-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "ap-southeast-2"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "ca-central-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "cn-north-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "cn-northwest-1"
              ]
            }
          ]
        },
        {
          "Fn::Or": [
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "eu-central-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "eu-north-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "eu-south-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "eu-west-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "eu-west-2"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "eu-west-3"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "me-south-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "sa-east-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "us-east-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "us-east-2"
              ]
            }
          ]
        },
        {
          "Fn::Or": [
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "us-west-1"
              ]
            },
            {
              "Fn::Equals": [
                {
                  "Ref": "AWS::Region"
                },
                "us-west-2"
              ]
            }
          ]
        }
      ]
    }
  },
  "Parameters": {
    "BootstrapVersion": {
      "Type": "AWS::SSM::Parameter::Value<String>",
      "Default": "/cdk-bootstrap/hnb659fds/version",
      "Description": "Version of the CDK Bootstrap resources in this environment, automatically retrieved from SSM Parameter Store. [cdk:skip]"
    }
  },
  "Rules": {
    "CheckBootstrapVersion": {
      "Assertions": [
        {
          "Assert": {
            "Fn::Not": [
              {
                "Fn::Contains": [
                  [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5"
                  ],
                  {
                    "Ref": "BootstrapVersion"
                  }
                ]
              }
            ]
          },
          "AssertDescription": "CDK bootstrap stack version 6 required. Please run 'cdk bootstrap' with a recent version of the CDK CLI."
        }
      ]
    }
  }
}
    ...
```
### Example output

```bash
$ checkov -f cdk.out/AppStack.template.json
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: 2.0.727

cloudformation scan results:

Passed checks: 3, Failed checks: 5, Skipped checks: 1

...

Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
        SKIPPED for resource: AWS::S3::Bucket.MyBucketF68F3FF0
        Suppress comment: Ensure the S3 bucket has access logging enabled
        File: /cfn.json:3-22
        Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-13-enable-logging

```
