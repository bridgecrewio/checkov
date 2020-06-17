[![checkov](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/web/images/checkov_by_bridgecrew.png)](#)


[![Maintained by Bridgecrew.io](https://img.shields.io/badge/maintained%20by-bridgecrew.io-blueviolet)](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![build status](https://github.com/bridgecrewio/checkov/workflows/build/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Abuild) 
[![security status](https://github.com/bridgecrewio/checkov/workflows/security/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=event%3Apush+branch%3Amaster+workflow%3Asecurity) 
[![code_coverage](https://raw.githubusercontent.com/bridgecrewio/checkov/master/coverage.svg?sanitize=true)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Acoverage)
[![docs](https://img.shields.io/badge/docs-passing-brightgreen)](https://www.checkov.io/documentation?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![PyPI](https://img.shields.io/pypi/v/checkov)](https://pypi.org/project/checkov/)
[![Downloads](https://pepy.tech/badge/checkov)](https://pepy.tech/project/checkov)
[![Terraform Version](https://img.shields.io/badge/tf-%3E%3D0.12.0-blue.svg)](#)

**Checkov** is a static code analysis tool for infrastructure-as-code. It scans cloud infrastructure provisioned using Terraform, Cloudformation or Kubernetes and detects security and compliance misconfigurations.


Checkov also powers [**Bridgecrew**](https://bridgecrew.io/), the developer-first platform that codifies and streamlines cloud security throughout the development lifecycle. Bridgecrew identifies, fixes, and prevents misconfigurations in cloud resources and infrastructure-as-code files. 

<a href="https://www.bridgecrew.cloud/login/signUp/?utm_campaign=checkov-github-repo&utm_source=github.com&utm_medium=get-started-button" title="Try_Bridgecrew">
    <img src="https://dabuttonfactory.com/button.png?t=Try+Bridgecrew&f=Open+Sans-Bold&ts=26&tc=fff&hp=45&vp=20&c=round&bgt=unicolored&bgc=662eff" align="right" width="120">
</a>


<a href="https://docs.bridgecrew.io?utm_campaign=checkov-github-repo&utm_source=github.com&utm_medium=read-docs-button" title="Docs">
    <img src="https://dabuttonfactory.com/button.png?t=Read+the+Docs&f=Open+Sans-Bold&ts=26&tc=fff&hp=45&vp=20&c=round&bgt=unicolored&bgc=662eff" align="right" width="120">
</a>

## **Table of contents**

- [Features](#features)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [Support](#support)

 ## Features

 * [300+ built-in policies](docs/3.Scans/resource-scans.md) cover security and compliance best practices for AWS, Azure & Google Cloud.
 * Scans Terraform, AWS CloudFormation and Kubernetes configuration files.
 * Detects [AWS credentials](docs/3.Scans/Credentials%20Scans.md) in EC2 Userdata, Lambda environment variables and Terrafrom providers 
 * Policies support evaluation of variables to their optional default value.
 * Supports in-line [suppression](docs/2.Concepts/Suppressions.md) of accepted risks or false-positives to reduce recurring scan failures. Also supports global skip from using CLI.
 * Output currently available as CLI, JSON or JUnit XML.

## Screenshots

Scan results in CLI

![scan-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/checkov-recording.gif)

Scheduled scan result in Jenkins

![jenikins-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/checkov-jenkins.png)

## Getting started

### Installation

```sh
pip install checkov
```

or using homebrew (MacOS only)

```sh
brew tap bridgecrewio/checkov https://github.com/bridgecrewio/checkov
brew update
brew install checkov
```

### Configure an input folder

```sh
checkov -d /user/path/to/iac/code
```

Or a specific file

```sh
checkov -f /user/tf/example.tf
```

or

```sh
checkov -f /user/cloudformation/example.yml
```

### Scan result sample (CLI)

```sh
Passed Checks: 1, Failed Checks: 1, Suppressed Checks: 0
Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/main.tf:
	 Passed for resource: aws_s3_bucket.template_bucket 
Check: "Ensure all data stored in the S3 bucket is securely encrypted at rest"
/../regionStack/main.tf:
	 Failed for resource: aws_s3_bucket.sls_deployment_bucket_name       
```

Start using Checkov by reading the [Getting Started](docs/1.Introduction/Getting%20Started.md) page.

### Using Docker

```sh
docker pull bridgecrew/checkov
docker run -t -v /user/tf:/tf bridgecrew/checkov -d /tf
```

### Suppressing/Ignoring a check

Like any static-analysis tool it is limited by its analysis scope. 
For example, if a resource is managed manually, or using subsequent configuration management tooling, 
a suppression can be inserted as a simple code annotation.

#### Suppression comment format

To skip a check on a given Terraform definition block or CloudFormation resource, apply the following comment pattern inside it's scope:

`checkov:skip=<check_id>:<suppression_comment>`

* `<check_id>` is one of the [available check scanners](docs/3.Scans/resource-scans.md)
* `<suppression_comment>` is an optional suppression reason to be included in the output

#### Example

The following comment skip the `CKV_AWS_20` check on the resource identified by `foo-bucket`, where the scan checks if an AWS S3 bucket is private.
In the example, the bucket is configured with a public read access; Adding the suppress comment would skip the appropriate check instead of the check to fail.

```hcl-terraform
resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
    #checkov:skip=CKV_AWS_20:The bucket is a public static content host
  bucket        = local.bucket_name
  force_destroy = true
  acl           = "public-read"
}
```

The output would now contain a ``SKIPPED`` check result entry:

```bash
...
...
Check: "S3 Bucket has an ACL defined which allows public access."
	SKIPPED for resource: aws_s3_bucket.foo-bucket
	Suppress comment: The bucket is a public static content host
	File: /example_skip_acl.tf:1-25
	
...
```

To suppress checks in Kubernetes manifests, annotations are used with the following format:
`checkov.io/skip#: <check_id>=<suppression_comment>`

For example: 

```bash
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

#### Logging

For detailed logging to stdout setup the environment variable `LOG_LEVEL` to `DEBUG`. 

Default is `LOG_LEVEL=WARNING`.

#### Skipping directories
To skip a whole directory, use the environment variable `CKV_IGNORED_DIRECTORIES`. 
Default is `CKV_IGNORED_DIRECTORIES=node_modules,.terraform,.serverless`

## Alternatives

For Terraform compliance scanners check out [tfsec](https://github.com/liamg/tfsec), [Terrascan](https://github.com/cesar-rodriguez/terrascan) and [Terraform AWS Secure Baseline](https://github.com/nozaq/terraform-aws-secure-baseline).

For CloudFormation scanning check out [cfripper](https://github.com/Skyscanner/cfripper/) and [cfn_nag](https://github.com/stelligent/cfn_nag).

For Kubernetes scanning check out [kube-scan](https://github.com/octarinesec/kube-scan) and [Polaris](https://github.com/FairwindsOps/polaris).

## Contributing

Contribution is welcomed! 

Start by reviewing the [contribution guidelines](CONTRIBUTING.md). After that, take a look at a [good first issue](https://github.com/bridgecrewio/checkov/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

Looking to contribute new checks? Learn how to write a new check (AKA policy) [here](docs/5.Contribution/New-Check.md).

## Support

[Bridgecrew](https://bridgecrew.io) builds and maintains Checkov to make policy-as-code simple and accessible. 

Start with our [Documentation](https://bridgecrewio.github.io/checkov/) for quick tutorials and examples.

If you need direct support you can contact us at info@bridgecrew.io .
