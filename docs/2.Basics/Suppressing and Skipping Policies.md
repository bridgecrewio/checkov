---
layout: default
published: true
title: Suppressing and Skipping Policies
nav_order: 3
---

# Suppressing/skipping

Like any static-analysis tool, suppression is limited by its analysis scope.
For example, if a resource is managed manually, or using configuration management tools, a suppression can be inserted as a simple code annotation.

There are two main ways to skip or suppress checks:

1. Suppress individual checks on a per-resource basis
2. Explicitly run or skip certain checks altogether

# Suppressing individual checks

You can use inline code comments or annotations to skip individual checks for a particular resource.

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

### Dockerfile Example
To suppress checks in Dockerfiles the comment can be addded to any line inside the file.

```dockerfile
#checkov:skip=CKV_DOCKER_5: no need to skip python check
#checkov:skip=CKV2_DOCKER_7: no need to skip graph check
FROM alpine:3.3
RUN apk --no-cache add nginx
EXPOSE 3000 80 443 22
#checkov:skip=CKV_DOCKER_1: required
CMD ["nginx", "-g", "daemon off;"]
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

### CloudFormation Metadata
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

### SCA
CVEs can be suppressed using `--skip-check CKV_CVE_2022_1234` to suppress a specific CVE for that run or `--skip-cve-package package` to skip all CVEs for a specific package.

For inline suppressions, depending on the package manager there are different ways to suppress CVEs. You can either suppress a CVE for all packages, all CVEs for a package or specific CVE for a package. Today, only requirements.txt is supported.

#### Python - requirements.txt
The skip comment can be anywhere

```requirements.txt
# checkov:skip=CVE-2019-19844: ignore CVE for all packages
# checkov:skip=jinja2: all CVEs for a package
# checkov:skip=django[CVE-2019-19844,CVE-2019-19844]: specific CVEs for a package
django==1.2
jinja2==3.1.0
```

# Specifying or skipping checks for the entire run

You can also fine-tune which checks run or do not run for the overall scan using the `--check` and `--skip-check` flags. You can use these flags to specify check IDs (or wildcards) and / or check severities (if using the platform integration). Any skipped check will simply not run at all and will not appear in the output. Other checks will run as normal (but may result in resource-level skips, as described above).

If you specify a severity with the `--check` flag, then any check that is equal to or greater than that severity will be included. If you specify a severity with the `--skip-check` flag, then any check less than or equal to that severity will be skipped.

You can also combine the `--check` and `--skip-check` flags when using severities to get a very granular policy set for the run. In this case, the `--check` filter will be applied first to explicitly include checks, and then the `--skip-check` list will be applied to remove any remaining checks. See below for examples.

In order to filter by severity, you must run with the platform integration via API key.

## Examples

Allow only the two specified checks to run: 
```sh
checkov --directory . --check CKV_AWS_20,CKV_AWS_57
```

Run all checks except the one specified:
```sh
checkov -d . --skip-check CKV_AWS_20
```

Run all checks except checks with specified patterns:
```sh
checkov -d . --skip-check CKV_AWS*
```

Run all checks that are MEDIUM severity or higher (requires API key):
```sh
checkov -d . --check MEDIUM --bc-api-key ...
```

Run all checks that are MEDIUM severity or higher, as well as check CKV_123 (assume this is a LOW severity check):
```sh
checkov -d . --check MEDIUM,CKV_123 --bc-api-key ...
```

Skip all checks that are MEDIUM severity or lower:
```sh
checkov -d . --skip-check MEDIUM --bc-api-key ...
```

Skip all checks that are MEDIUM severity or lower, as well as check CKV_789 (assume this is a high severity check):
```sh
checkov -d . --skip-check MEDIUM,CKV_789 --bc-api-key ...
```

Run all checks that are MEDIUM severity or higher, but skip check CKV_123 (assume this is a medium or higher severity check):
```sh
checkov -d . --check MEDIUM --skip-check CKV_123 --bc-api-key ...
```

Run check CKV_789, but skip it if it is a medium severity (the --check logic is always applied before --skip-check)
```sh
checkov -d . --skip-check MEDIUM --check CKV_789 --bc-api-key ...
```

For Kubernetes workloads, you can also use allow/deny namespaces.  For example, do not report any results for the 
kube-system namespace:
```sh
checkov -d . --skip-check kube-system
```

# Platform enforcement rules

Checkov can download [enforcement rules](https://docs.bridgecrew.io/docs/enforcement) that you configure in the Bridgecrew or Prisma Cloud platform. This allows you to centralize the failure and check threshold configurations, instead of defining them in each pipeline.

To use enforcement rules, use the `--use-enforcement-rules` flag along with a platform API key.

Enforcement rules allow you to specify a severity soft-fail threshold equivalent to using the `--check <SEVERITY>` argument in Checkov. Note that the enforcement rule "soft fail" option is different from the `--soft-fail` options in Checkov. The enforcement rule setting specifies a threshold such that any lower severity policies get skipped, so it is equivalent to the `--check` option. However, whereas this argument is global, the enforcement rules settings are more granular, for each major category of scanner that Checkov has (IaC, secrets, etc). So, for example, you can set the soft-fail level any IaC scan to `MEDIUM` severity or higher (skip all `LOW`), and hard-fail the SCA scan on `HIGH` severity or higher (skip all `MEDIUM` and lower).

You can combine the platform enforcement rules with the `--check` and `---skip-check` arguments to customize the options for a specific run. It will have the following effects. Note that these flags are still global and will get merged with the relevant enforcement rule for the particular framework being scanned.

* If you use `--check` and / or `--skip-check` with only check IDs (not severities), then it combines those lists with the soft fail threshold from the enforcement rule.
* If you use `--check` and / or `--skip-check` with a severity, then those severities override the enforcement rule soft fail threshold for all runners.
