---
layout: default
published: true
title: Suppressing and Skipping Policies
nav_order: 3
---

# Suppressing/skipping

Like any static-analysis tool, suppression is limited by its analysis scope.
For example, if a resource is managed manually, or using configuration management tools, a suppression can be inserted as a simple code annotation.

## Suppression Comment Format

To skip a check on a given Terraform definition block or CloudFormation resource, apply the following comment pattern inside its scope:
`checkov:skip=<check_id>:<suppression_comment>`

* `<check_id>` is one of the available check scanners.
* `<suppression_comment>` is an optional suppression reason to be included in the output.

### Example
The following comment skips the `CKV_AWS_20` check on the resource identified by `foo-bucket`, where the scan checks if an AWS S3 bucket is private.
In the example, the bucket is configured with a public read access; Adding the suppression comment skips the appropriate check instead of the check failing.

```python
resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
    #checkov:skip=CKV_AWS_20:The bucket is a public static content host
  bucket        = local.bucket_name
  force_destroy = true
  acl           = "public-read"
}
```

The output now contains a ``SKIPPED`` check result entry:

```python
...
...
Check: "S3 Bucket has an ACL defined which allows public access."
	SKIPPED for resource: aws_s3_bucket.foo-bucket
	Suppress comment: The bucket is a public static content host
	File: /example_skip_acl.tf:1-25

...
```
### Cloudformation Example:

```yaml
Resources:
  MyDB:
    Type: 'AWS::RDS::DBInstance'
    # Test case for check skip via comment
    # checkov:skip=CKV_AWS_16:Ensure all data stored in the RDS is securely encrypted at rest
    Properties:
      DBName: 'mydb'
      DBInstanceClass: 'db.t3.micro'
      Engine: 'mysql'
      MasterUsername: 'master'
      MasterUserPassword: 'password'
```

### Kubernetes Example
To suppress checks in Kubernetes manifests, annotations are used with the following format:
`checkov.io/skip#: <check_id>=<suppression_comment>`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
  annotations:
    checkov.io/skip1: CKV_K8S_20=I don't care about Privilege Escalation :-O
    checkov.io/skip2: CKV_K8S_14
    checkov.io/skip3: CKV_K8S_11=I have not set CPU limits as I want BestEffort QoS
spec:
  containers:
...
```

### Secrets Example
To suppress secrets checks in any configuration file a comment needs to be added directly before, after or next to the infringing line.

```yaml
Resources:
  MyDB:
    Type: 'AWS::RDS::DBInstance'
    Properties:
      DBName: 'mydb'
      DBInstanceClass: 'db.t3.micro'
      Engine: 'mysql'
      MasterUsername: 'master'
      # checkov:skip=CKV_SECRET_6 before it
      MasterUserPassword: 'password' # checkov:skip=CKV_SECRET_6 or next to it
      # checkov:skip=CKV_SECRET_6 or after it
```

## CloudFormation Metadata
Additionally, it is possible to suppress CloudFormation checks via the `Metadata` section inside a resource.
```yaml
Resources:
  MyDB:
    Metadata:
      checkov:
        skip:
          - id: "CKV_AWS_157"
            comment: "Ensure that RDS instances have Multi-AZ enabled"
    Type: "AWS::RDS::DBInstance"
    Properties:
      DBName: "mydb"
      DBInstanceClass: "db.t3.micro"
      Engine: "mysql"
      MasterUsername: "master"
      MasterUserPassword: "password"
```

### CDK Example
The `Metadata` section of a CDK construct can only be adjusted via the L1 (layer 1) construct, also known as CloudFormation resource.
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
        'comment': 'Ensure the S3 bucket has access logging enabled'
      }
    ]
  }
}
```
Run the `synth` command to generate a CloudFormation template and scan it
```shell
$ cdk synth
Resources:
  MyBucketF68F3FF0:
    Type: AWS::S3::Bucket
    Properties:
      VersioningConfiguration:
        Status: Enabled
    UpdateReplacePolicy: Retain
    DeletionPolicy: Retain
    Metadata:
      checkov:
        skip:
          - id: CKV_AWS_18
            comment: Ensure the S3 bucket has access logging enabled
  CDKMetadata:
    ...

$ checkov -f cdk.out/AppStack.template.json
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By bridgecrew.io | version: 2.0.727

cloudformation scan results:

Passed checks: 3, Failed checks: 5, Skipped checks: 1

...

Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
        SKIPPED for resource: AWS::S3::Bucket.MyBucketF68F3FF0
        Suppress comment: Ensure the S3 bucket has access logging enabled
        File: /../anton/cfn.json:3-22
        Guide: https://docs.bridgecrew.io/docs/s3_13-enable-logging


```
