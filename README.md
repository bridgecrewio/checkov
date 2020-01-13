# Checkov

[![Maintained by Bridgecrew.io](https://img.shields.io/badge/maintained%20by-bridgecrew.io-blueviolet)](https://bridgecrew.io)
[![build status](https://github.com/bridgecrewio/checkov/workflows/build/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Abuild) 
[![code_coverage](https://raw.githubusercontent.com/bridgecrewio/checkov/master/coverage.svg?sanitize=true)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Acoverage)
[![docs](https://img.shields.io/badge/docs-passing-brightgreen)](https://www.checkov.io/documentation)
[![PyPI](https://img.shields.io/pypi/v/checkov)](https://pypi.org/project/checkov/)
[![Downloads](https://pepy.tech/badge/checkov)](https://pepy.tech/project/checkov)
![Terraform Version](https://img.shields.io/badge/tf-%3E%3D0.12.0-blue.svg)

## **Table of contents**
- [Description](#description)
- [Features](#features)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [Support](#support)

## Description
Checkov is a static code analysis tool for infrastructure-as-code. It scans cloud infrastructure provisioned using Terraform and detects security and compliance misconfigurations. 

Checkov is written in Python and provides a simple method to write and manage policies. It follows the CIS Foundations benchmarks where applicable.

 ## Features

 * [50+ built-in policies](docs/3.Scans/resource-scans.md) cover security and compliance best practices for AWS, Azure & Google Cloud.
 * Policies support variable scanning by building a dynamic code dependency graph (coming soon).
 * Supports in-line suppression of accepted risks or false-positives to reduce recurring scan failures.
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

### Configure an input folder

```sh
checkov -d /user/tf
```
Or a specific file
```sh
checkov -f /user/tf/example.tf
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
docker run bridgecrew/checkov -i -v /user/tf:/tf -d /tf
```

## Alternatives

For Terraform compliance scanners check out [tfsec](https://github.com/liamg/tfsec), [Terrascan](https://github.com/cesar-rodriguez/terrascan) and [Terraform AWS Secure Baseline](https://github.com/nozaq/terraform-aws-secure-baseline).

For CloudFormation scanning check out [cfripper](https://github.com/Skyscanner/cfripper/) and [cfn_nag](https://github.com/stelligent/cfn_nag).

## Contributing
Contribution is welcomed! 

Start by reviewing the [contribution guidelines](CONTRIBUTING.md). After that, take a look at a [good first issue](https://github.com/bridgecrewio/checkov/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

Looking to contribute new checks? Learn how to write a new check (AKA policy) [here](docs/5.Contribution/New-Check.md)

## Support

[Bridgecrew](https://bridgecrew.io) builds and maintains Checkov to make policy-as-code simple and accessible. 

Start with our [Documentation](https://bridgecrewio.github.io/checkov/) for quick tutorials and examples.

If you need direct support you can contact us at info@bridgecrew.io or [open a ticket](https://bridgecrew.zendesk.com/hc/en-us/requests/new).
