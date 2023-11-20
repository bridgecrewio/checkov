---
layout: default
published: true
title: Cloudformation configuration scanning
nav_order: 20
---

# Cloudformation configuration scanning
Checkov supports the evaluation of policies on your Cloudformation files.
When using checkov to scan a directory that contains a Cloudformation template it will validate if the file is compliant with AWS best practices such as making sure S3 buckets are encrypted, HTTPS is being used, and more.  

Full list of Cloudformation policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/cloudformation.html).


### Example misconfigured Cloudformation

```yaml
Resources:
  MyDB0:
    Type: 'AWS::RDS::DBInstance'
    Properties:
      DBName: 'mydb'
      DBInstanceClass: 'db.t3.micro'
      Engine: 'mysql'
      MasterUsername: 'master'
      MasterUserPassword: 'password'
  MyDB1:
    Type: 'AWS::RDS::DBInstance'
    Properties:
      DBName: 'mydb'
      DBInstanceClass: 'db.t3.micro'
      Engine: 'mysql'
      MasterUsername: 'master'
      MasterUserPassword: 'password'
      StorageEncrypted: false

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
                                      
By Prisma Cloud | version: 2.0.723 

cloudformation scan results:

Passed checks: 2, Failed checks: 6, Skipped checks: 0

Check: CKV_AWS_17: "Ensure all data stored in RDS is not publicly accessible"
   PASSED for resource: AWS::RDS::DBInstance.MyDB0
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:2-9
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/public-policies/public-2

Check: CKV_AWS_17: "Ensure all data stored in RDS is not publicly accessible"
   PASSED for resource: AWS::RDS::DBInstance.MyDB1
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:10-18
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/public-policies/public-2

Check: CKV_AWS_161: "Ensure RDS database has IAM authentication enabled"
   FAILED for resource: AWS::RDS::DBInstance.MyDB0
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:2-9
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/ensure-rds-database-has-iam-authentication-enabled

      2 |   MyDB0:
      3 |     Type: 'AWS::RDS::DBInstance'
      4 |     Properties:
      5 |       DBName: 'mydb'
      6 |       DBInstanceClass: 'db.t3.micro'
      7 |       Engine: 'mysql'
      8 |       MasterUsername: 'master'
      9 |       MasterUserPassword: 'password'


Check: CKV_AWS_157: "Ensure that RDS instances have Multi-AZ enabled"
   FAILED for resource: AWS::RDS::DBInstance.MyDB0
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:2-9
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-73

      2 |   MyDB0:
      3 |     Type: 'AWS::RDS::DBInstance'
      4 |     Properties:
      5 |       DBName: 'mydb'
      6 |       DBInstanceClass: 'db.t3.micro'
      7 |       Engine: 'mysql'
      8 |       MasterUsername: 'master'
      9 |       MasterUserPassword: 'password'


Check: CKV_AWS_16: "Ensure all data stored in the RDS is securely encrypted at rest"
   FAILED for resource: AWS::RDS::DBInstance.MyDB0
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:2-9
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-4

      2 |   MyDB0:
      3 |     Type: 'AWS::RDS::DBInstance'
      4 |     Properties:
      5 |       DBName: 'mydb'
      6 |       DBInstanceClass: 'db.t3.micro'
      7 |       Engine: 'mysql'
      8 |       MasterUsername: 'master'
      9 |       MasterUserPassword: 'password'


Check: CKV_AWS_161: "Ensure RDS database has IAM authentication enabled"
   FAILED for resource: AWS::RDS::DBInstance.MyDB1
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:10-18
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/ensure-rds-database-has-iam-authentication-enabled

      10 |   MyDB1:
      11 |     Type: 'AWS::RDS::DBInstance'
      12 |     Properties:
      13 |       DBName: 'mydb'
      14 |       DBInstanceClass: 'db.t3.micro'
      15 |       Engine: 'mysql'
      16 |       MasterUsername: 'master'
      17 |       MasterUserPassword: 'password'
      18 |       StorageEncrypted: false


Check: CKV_AWS_157: "Ensure that RDS instances have Multi-AZ enabled"
   FAILED for resource: AWS::RDS::DBInstance.MyDB1
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:10-18
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-73

      10 |   MyDB1:
      11 |     Type: 'AWS::RDS::DBInstance'
      12 |     Properties:
      13 |       DBName: 'mydb'
      14 |       DBInstanceClass: 'db.t3.micro'
      15 |       Engine: 'mysql'
      16 |       MasterUsername: 'master'
      17 |       MasterUserPassword: 'password'
      18 |       StorageEncrypted: false


Check: CKV_AWS_16: "Ensure all data stored in the RDS is securely encrypted at rest"
   FAILED for resource: AWS::RDS::DBInstance.MyDB1
   File: /example_RDSEncryption/RDSEncryption-FAIL.yaml:10-18
   Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-4

      10 |   MyDB1:
      11 |     Type: 'AWS::RDS::DBInstance'
      12 |     Properties:
      13 |       DBName: 'mydb'
      14 |       DBInstanceClass: 'db.t3.micro'
      15 |       Engine: 'mysql'
      16 |       MasterUsername: 'master'
      17 |       MasterUserPassword: 'password'
      18 |       StorageEncrypted: false



```

## The Cloudformation Graph
Checkov follows the CFN [template reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html) where some resource can have an attribute reference that will result in the final state, or a resource can have a dependency in another resource.  

For example the following code:
```yaml
Description: My super cool Lambda
Parameters:
  ParamTracingConfig:
    Description: Active tracing config
    Type: String
    Default: "PassThrough"
Resources:
  WrongTracingConfigValueLambdaFunctionWithRef:
    Type: "AWS::Lambda::Function"
    Properties:
      FunctionName: !Sub "${AWS::AccountId}-${CompanyName}-${Environment}-analysis"
      Runtime: nodejs12.x
      Role: !GetAtt IAM4Lambda.Arn
      Handler: exports.test
      Code:
        ZipFile: |
          console.log("Hello World");
      Tags:
        - Key: Name
          Value: !Sub "${AWS::AccountId}-${CompanyName}-${Environment}-analysis"
        - Key: Environment
          Value: !Sub "${AWS::AccountId}-${CompanyName}-${Environment}"
      Tracing_config:
        Mode: !Ref ParamTracingConfig

```

Contains the lambda resource that has the attribute `Tracing_config` that references the value of the parameter `ParamTracingConfig`. Those references are computes in a graph connecting the different cfn elements so we would be able to analyze if the parameter that is compliant or not with best practices.   
