---
layout: default
published: true
title: JUnit XML
nav_order: 20
---

# JUnit XML

JUnit is the most widespread testing framework for Java and offers its result as an XML output, mostly known as JUnit XML.
This output is often used to show the test results in CI tools like Jenkins or Gitlab.

A typical output looks like this
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<testsuites>
  <testsuite errors="0" failures="0" hostname="myhost" id="0" name="TestMessage" package="com.sample.test" skipped="0" tests="1" time="0.063" timestamp="2015-01-13T07:23:07">
      <properties>
      </properties>
      <testcase classname="com.sample.test.TestMessage" name="test_welcome_message" time="0.002" />
      <system-out><![CDATA[]]></system-out>
      <system-err><![CDATA[]]></system-err>
  </testsuite>
  <testsuite errors="0" failures="0" hostname="myhost" id="1" name="TestMessage2" package="com.sample.test" skipped="0" tests="2" time="0.06" timestamp="2015-01-13T07:23:08">
      <properties>
      </properties>
      <testcase classname="com.sample.test.TestMessage2" name="test_welcome_message_2" time="0.001" />
      <testcase classname="com.sample.test.TestMessage2" name="test_welcome_message_3" time="0.003" />
      <system-out><![CDATA[]]></system-out>
      <system-err><![CDATA[]]></system-err>
  </testsuite>
</testsuites>
```

## Structure

Further information on the different elements and attributes can be found [here](https://llg.cubic.org/docs/junit/).

### testsuite

Each testsuite stores the results of one `checkov` runner.

```xml
<testsuite disabled="0" errors="0" failures="2" name="terraform scan" skipped="1" tests="5" time="12.34">
```

- `name`: Name of the runner
- `tests`: Amount of runned checks (passed + failed + skipped)
- `failures`: Amount of failed checks
- `skipped`: Amount of skipped checks
- `time`: Currently not used - At some point it will store the time the runner needed to execute all checks
- `disabled`: Not used - Was introduced in JUnit 5 to mark disabled tests
- `errors`: Not used - Amount of tests with real exceptions

### properties

The properties block stores the used flags during a `checkov` run. 

```xml
<properties>
    <property name="directory" value="example"/>
</properties>
```

- `name`: Name of the flag used
- `value`: Value passed to the flag, otherwise `""`

### testcase

A testcase represents the result of a check.

IaC
```xml
<testcase name="[CRITICAL][CKV_AWS_20] S3 Bucket has an ACL defined which allows public READ access." classname="/main.tf.aws_s3_bucket.example" file="/main.tf"/>
```

- `name`: Format `[<severity>][<check ID>] <check name>`
- `classname`: Format `<fiel path>.<resource ID>`
- `file`: Used by Gitlab - File path of the scanned file

SCA
```xml
<testcase name="[HIGH][CVE-2013-7370] connect: 2.6.0" classname="/package-lock.json.connect" file="/package-lock.json">
```

- `name`: Format `[<severity>][<CVE ID>] <package name>: <package version>`
- `classname`: Format `<fiel path>.<package name>`
- `file`: Used by Gitlab - File path of the scanned file

NOTE: For none API token user severity will be `[NONE]`

#### failure

A failure block stores the error lines of the check.

IaC
```xml
<failure type="failure" message="Ensure all data stored in the S3 bucket have versioning enabled">
    Resource: aws_s3_bucket.example
    File: /main.tf: 6-9
    Guideline: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_16-enable-versioning
    
        6 | resource "aws_s3_bucket" "example" {
        7 |   # checkov:skip=CKV_AWS_18: logging not needed on a logging bucket
        8 |   bucket = "test-12345"
        9 | }
</failure>
```

- `message`: Format `<check name>`
- `content`: Format
  ```
  Resource: <resource ID>
  File: <file path>
  Guideline: <guideline link>
  
    <line numbers + code of failed resource>
  ```

SCA
```xml
<failure type="failure" message="CVE-2013-7370 found in connect: 2.6.0">
    Description: A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c for Go allows remote attackers to cause a denial of service against SSH servers.
    Link: https://nvd.nist.gov/vuln/detail/CVE-2020-29652
    Published Date: 2020-12-17T21:31:00+02:00
    Base Score: 7.5
    Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H
    Risk Factors: ["Has fix", "High severity", "Attack complexity: low", "Attack vector: network", "DoS"]
    Fix Details:
      Status: fixed in 2.8.1 
      Fixed Version: 2.8.1
  
    Resource: package-lock.json.connect
    File: /package-lock.json: 0-0
    
        0 | connect: 2.6.0
</failure>
```

- `message`: Format `<CVE ID> found in <package name>: <package version>`
- `content`: Format
  ```
  Description: <CVE description>
  Link: <CVE link>
  Vector: <CVSS vector string>
  Risk Factors: <list of risk factors>
  Fix Details:
    Status: <status of possible fixed versions>
    Fixed Version: <lowest fixed version>
  
  Resource: <resource ID>
  File: <file path>
  
    <line numbers + code of vulnerable package>
  ```
  
NOTE: We currently don't parse the scanned parse files, therefore the line numbers and code representation are generated.

#### skipped

A skipped block stores the skip comment defined for the check.

IaC
```xml
<skipped type="skipped" message="logging not needed on a logging bucket"/>
```

- `message`: Content of the skip comment

SCA
```xml
<skipped type="skipped" message="CVE-2019-19844 skipped for django: 1.2"/>
```

- `message`: Format `<CVE ID> skipped for <package name>: <package version>`

## Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites disabled="0" errors="0" name="checkov" failures="2" tests="6" time="23.34">
    <testsuite disabled="0" errors="0" failures="2" name="terraform scan" skipped="1" tests="5" time="12.34">
        <properties>
            <property name="directory" value="example"/>
            <property name="output" value="['junitxml']"/>
        </properties>

        <testcase name="[CRITICAL][CKV_AWS_20] S3 Bucket has an ACL defined which allows public READ access." classname="/main.tf.aws_s3_bucket.example" file="/main.tf"/>
        <testcase name="[CRITICAL][CKV_AWS_20] S3 Bucket has an ACL defined which allows public READ access." classname="/main.tf.aws_s3_bucket.example_2" file="/main.tf"/>

        <testcase name="[HIGH][CKV_AWS_21] Ensure all data stored in the S3 bucket have versioning enabled" classname="/main.tf.aws_s3_bucket.example" file="/main.tf">
            <failure type="failure" message="Ensure all data stored in the S3 bucket have versioning enabled">
                Resource: aws_s3_bucket.example
                File: /main.tf: 6-9
                Guideline: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_16-enable-versioning
                
                    6 | resource "aws_s3_bucket" "example" {
                    7 |   # checkov:skip=CKV_AWS_18: logging not needed on a logging bucket
                    8 |   bucket = "test-12345"
                    9 | }
            </failure>
        </testcase>
        <testcase name="[HIGH][CKV_AWS_21] Ensure all data stored in the S3 bucket have versioning enabled" classname="/main.tf.aws_s3_bucket.example_2" file="/main.tf">
            <failure type="failure" message="Ensure all data stored in the S3 bucket have versioning enabled">
                Resource: aws_s3_bucket.example_2
                File: /main.tf: 12-15
                Guideline: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_16-enable-versioning
                
                    12 | resource "aws_s3_bucket" "example_2" {
                    13 |   # checkov:skip=CKV_AWS_18: logging not needed on a logging bucket
                    14 |   bucket = "test-12345"
                    15 | }
            </failure>
        </testcase>

        <testcase name="[MEDIUM][CKV_AWS_18] Ensure the S3 bucket has access logging enabled" classname="/main.tf.aws_s3_bucket.example" file="/main.tf">
            <skipped type="skipped" message="logging not needed on a logging bucket"/>
        </testcase>
    </testsuite>
    <testsuite disabled="0" errors="0" failures="0" name="cloudformation scan" skipped="0" tests="1" time="1.00">
        <testcase name="[LOW][CKV_AWS_20] S3 Bucket has an ACL defined which allows public READ access." classname="/cfn.yaml.AWS::S3::Bucket.Example" file="/cfn.yaml"/>
    </testsuite>
    <testsuite disabled="0" errors="0" failures="2" name="sca_package scan" skipped="1" tests="3" time="10.00">
        <testcase name="[HIGH][CVE-2013-7370] connect: 2.6.0" classname="/package-lock.json.connect" file="/package-lock.json">
            <failure type="failure" message="CVE-2013-7370 found in connect: 2.6.0">
                Description: A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c for Go allows remote attackers to cause a denial of service against SSH servers.
                Link: https://nvd.nist.gov/vuln/detail/CVE-2020-29652
                Published Date: 2020-12-17T21:31:00+02:00
                Base Score: 7.5
                Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H
                Risk Factors: ["Has fix", "High severity", "Attack complexity: low", "Attack vector: network", "DoS"]
                Fix Details:
                  Status: fixed in 2.8.1 
                  Fixed Version: 2.8.1

                Resource: package-lock.json.connect
                File: /package-lock.json: 0-0
                
                    0 | connect: 2.6.0
            </failure>
        </testcase>

        <testcase name="[HIGH][CVE-2013-7370] django: 1.2" classname="/requirements.txt.django" file="/requirements.txt">
            <skipped type="skipped" message="CVE-2019-19844 skipped for django: 1.2"/>
        </testcase>
    </testsuite>
</testsuites>
```
