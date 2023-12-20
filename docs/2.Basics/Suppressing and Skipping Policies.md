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
                                      
By Prisma Cloud | version: 3.0.1

cloudformation scan results:

Passed checks: 3, Failed checks: 5, Skipped checks: 1

...

Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
        SKIPPED for resource: AWS::S3::Bucket.MyBucketF68F3FF0
        Suppress comment: Ensure the S3 bucket has access logging enabled
        File: /../anton/cfn.json:3-22
        Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-13-enable-logging


```

### Software Composition Analysis (SCA)
Suppressing SCA findings can be done in a variety of ways to fit your needs. CVEs can be suppressed using `--skip-check CKV_CVE_2022_1234` to suppress a specific CVE for that run or `--skip-cve-package package_name` to skip all CVEs for a specific package.

For inline SCA suppressions, depending on the package manager, there are different ways to suppress CVEs and License violations. Adding a skip comment to any package manager file will suppress all findings for that CVE or package and License combination for that file.

#### Python (requirements.txt), .NET (Paket), Java/Kotlin (gradle.properties), Ruby (Gemfile)
The skip comment can be anywhere in the file.

The example below is for requirements.txt

```requirements.txt
# checkov:skip=CVE-2019-19844: ignore CVE-2019-19844 for all packages in this file
# checkov:skip=jinja2[BC_LIC_1]: ignore non-OSI license violations for jinja2
django==1.2
jinja2==3.1.0
```

#### JavaScript (package.json and bower.json)
The skip comment can be anywhere in the metadata. Add these skip comments to the non-lock file and ensure you scan the non-lock file with any lock file scan. For example, package.json and yarn.lock must be scanned together for the suppression from the package.json to apply to the yarn.lock violations.

The example below is for multiple skip comments for package.json

```package.json
{
  "name": "my-package",
  "version": "1.0.0",
  "description": "A sample package.json file",
  "//": ["checkov:skip=express[BC_LIC_2]: ignore unknown license violations for express in this file",
         "checkov:skip=CVE-2023-123: ignore this CVE for this file"]
  "dependencies": {
    "express": "4.17.1",
    "lodash": "4.17.21"
  },
  "scripts": {
    "start": "node server.js",
    "test": "jest"
  }
}
```

Alternatively, you can add a single skip comment

```
"//": "checkov:skip=CVE-2023-123: ignore this CVE for this file"
```

### Java (pom.xml), .NET (*.csproj)
The skip comment can be anywhere in the file.

The example below is for pom.xml

```pom.xml
  <!--checkov:skip=CVE-2023-123: ignore this CVE for the file-->
  <!--checkov:skip=junit[BC_LIC_1]: ignore non-compliant license findings for junit-->
  <dependencies>
    <dependency>
      <groupId>org.springframework</groupId>
      <artifactId>spring-web</artifactId>
      <version>5.3.9</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
```

### Java/Kotlin (build.gradle), Go (go.mod)
The skip comment can be anywhere in the file. Adding skips to the go.mod file will apply to the go.sum file.

The example below is for go.mod

```go.mod
module example.com/myproject

go 1.17

require (
    github.com/gin-gonic/gin v1.7.4
    github.com/go-sql-driver/mysql v1.6.0
    //checkov:skip=CVE-2023-123: ignore this CVE for this file
    //checkov:skip=github.com/go-sql-driver/mysql[BC_LIC_2]: ignore unknown license violations for express in this file
)
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

Checkov can download [enforcement rules](https://docs.prismacloud.io/en/enterprise-edition/content-collections/application-security/risk-management/monitor-and-manage-code-build/enforcement) that you configure in Prisma Cloud. This allows you to centralize the failure and check threshold configurations, instead of defining them in each pipeline.

To use enforcement rules, use the `--use-enforcement-rules` flag along with a platform API key.

Enforcement rules allow you to specify a severity soft-fail threshold equivalent to using the `--check <SEVERITY>` argument in Checkov. Note that the enforcement rule "soft fail" option is different from the `--soft-fail` options in Checkov. The enforcement rule setting specifies a threshold such that any lower severity policies get skipped, so it is equivalent to the `--check` option. However, whereas this argument is global, the enforcement rules settings are more granular, for each major category of scanner that Checkov has (IaC, secrets, etc). So, for example, you can set the soft-fail level any IaC scan to `MEDIUM` severity or higher (skip all `LOW`), and hard-fail the SCA scan on `HIGH` severity or higher (skip all `MEDIUM` and lower).

You can combine the platform enforcement rules with the `--check` and `---skip-check` arguments to customize the options for a specific run. It will have the following effects. Note that these flags are still global and will get merged with the relevant enforcement rule for the particular framework being scanned.

* If you use `--check` and / or `--skip-check` with only check IDs (not severities), then it combines those lists with the soft fail threshold from the enforcement rule.
* If you use `--check` and / or `--skip-check` with a severity, then those severities override the enforcement rule soft fail threshold for all runners.
