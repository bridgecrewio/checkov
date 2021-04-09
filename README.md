[![checkov](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/web/images/checkov_by_bridgecrew.png)](#)
       
[![Maintained by Bridgecrew.io](https://img.shields.io/badge/maintained%20by-bridgecrew.io-blueviolet)](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![build status](https://github.com/bridgecrewio/checkov/workflows/build/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Abuild)
[![security status](https://github.com/bridgecrewio/checkov/workflows/security/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=event%3Apush+branch%3Amaster+workflow%3Asecurity) 
[![code_coverage](https://raw.githubusercontent.com/bridgecrewio/checkov/master/coverage.svg?sanitize=true)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Acoverage) 
[![docs](https://img.shields.io/badge/docs-passing-brightgreen)](https://www.checkov.io/documentation?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![PyPI](https://img.shields.io/pypi/v/checkov)](https://pypi.org/project/checkov/)
[![Python Version](https://img.shields.io/github/pipenv/locked/python-version/bridgecrewio/checkov)](#)
[![Terraform Version](https://img.shields.io/badge/tf-%3E%3D0.12.0-blue.svg)](#)
[![Downloads](https://pepy.tech/badge/checkov)](https://pepy.tech/project/checkov)
[![slack-community](https://slack.bridgecrew.io/badge.svg)](https://slack.bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
 

**Checkov** is a static code analysis tool for infrastructure-as-code.

It scans cloud infrastructure provisioned using [Terraform](https://terraform.io/), Terraform plan, [Cloudformation](https://aws.amazon.com/cloudformation/), [Kubernetes](https://kubernetes.io/), [Dockerfile](https://www.docker.com/),  [Serverless](https://www.serverless.com/) or [ARM Templates](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/overview) and detects security and compliance misconfigurations using graph-based scanning.
 
Checkov also powers [**Bridgecrew**](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov), the developer-first platform that codifies and streamlines cloud security throughout the development lifecycle. Bridgecrew identifies, fixes, and prevents misconfigurations in cloud resources and infrastructure-as-code files. 

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
- [Disclaimer](#disclaimer)
- [Support](#support)

 ## Features

 * [Over 750 built-in policies](docs/3.Scans/resource-scans.md) cover security and compliance best practices for AWS, Azure and Google Cloud.
 * Scans Terraform, Terraform Plan, CloudFormation, Kubernetes, Dockerfile, Serverless framework and ARM template files.
 * Supports Context-awareness policies based on in-memory graph-based scanning.
 * Supports Python format for attribute policies and YAML format for both attribute and composite policies.
 * Detects [AWS credentials](docs/3.Scans/Credentials%20Scans.md) in EC2 Userdata, Lambda environment variables and Terraform providers.
 * Evaluates [Terraform Provider](https://registry.terraform.io/browse/providers) settings to regulate the creation, management, and updates of IaaS, PaaS or SaaS managed through Terraform.
 * Policies support evaluation of [variables](docs/2.Concepts/Evaluations.md) to their optional default value.
 * Supports in-line [suppression](docs/2.Concepts/Suppressions.md) of accepted risks or false-positives to reduce recurring scan failures. Also supports global skip from using CLI.
* [Output](docs/1.Introduction/Results.md) currently available as CLI, JSON, JUnit XML and github markdown and link to remediation [guides](https://docs.bridgecrew.io/docs/aws-policy-index).
 
## Screenshots

Scan results in CLI

![scan-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/checkov-recording.gif)

Scheduled scan result in Jenkins

![jenikins-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/checkov-jenkins.png)

## Getting started

### Requrirements
 * Python >= 3.7 (Data classes are available for Python 3.7+)
 * Terraform >= 0.12

### Installation


```sh
pip3 install checkov
```

Installation on Alpine:
```sh
pip3 install --upgrade pip && pip3 install --upgrade setuptools
pip3 install checkov
```

Installation on Ubuntu 18.04 LTS:

Ubuntu 18.04 ships with Python 3.6. Install python 3.7 (from ppa repository)

```sh
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
sudo apt install python3-pip
sudo python3.7 -m pip install -U checkov #to install or upgrade checkov)
```

or using homebrew (MacOS only)

```sh
brew install checkov
```

or

```sh
brew upgrade checkov
```

### Upgrade

if you installed checkov with pip3
```sh
pip3 install -U checkov
```

### Configure an input folder or file

```sh
checkov --directory /user/path/to/iac/code
```

Or a specific file or files

```sh
checkov --file /user/tf/example.tf
```
Or
```sh
checkov -f /user/cloudformation/example1.yml -f /user/cloudformation/example2.yml
```

Or a terraform plan file in json format
```sh
terraform init
terraform plan -out tf.plan
terraform show -json tf.plan  > tf.json 
checkov -f tf.json
```
Note: `terraform show` output  file `tf.json` will be single line. 
For that reason all findings will be reported line number 0 by checkov
```sh
check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enabled"
	FAILED for resource: aws_s3_bucket.customer
	File: /tf/tf.json:0-0
	Guide: https://docs.bridgecrew.io/docs/s3_16-enable-versioning
  ```

If you have installed `jq` you can convert json file into multiple lines with the following command:
```sh
terraform show -json tf.plan | jq '.' > tf.json 
```
Scan result would be much user friendly.

```sh
checkov -f tf.json
Check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enabled"
	FAILED for resource: aws_s3_bucket.customer
	File: /tf/tf1.json:224-268
	Guide: https://docs.bridgecrew.io/docs/s3_16-enable-versioning

		225 |               "values": {
		226 |                 "acceleration_status": "",
		227 |                 "acl": "private",
		228 |                 "arn": "arn:aws:s3:::mybucket",

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
docker run --tty --volume /user/tf:/tf bridgecrew/checkov --directory /tf
```
Note: if you are using Python 3.6(Default version in Ubuntu 18.04) checkov will not work and it will fail with `ModuleNotFoundError: No module named 'dataclasses'`  error message. In this case, you can use the docker version instead.

Note that there are certain cases where redirecting `docker run --tty` output to a file - for example, if you want to save the Checkov JUnit output to a file - will cause extra control characters to be printed. This can break file parsing. If you encounter this, remove the `--tty` flag.

### Running or skipping checks 

Using command line flags you can specify to run only named checks (allow list) or run all checks except 
those listed (deny list).

List available checks:
```sh
checkov --list 
```

Allow only 2 checks to run: 
```sh
checkov --directory . --check CKV_AWS_20,CKV_AWS_57
```

Run all checks except 1 specified:
```sh
checkov -d . --skip-check CKV_AWS_52
```

Run all checks except checks with specified patterns:
```sh
checkov -d . --skip-check CKV_AWS*
```

For Kubernetes workloads, you can also use allow/deny namespaces.  For example, do not report any results for the 
kube-system namespace:
```sh
checkov -d . --skip-check kube-system
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
To skip multiple checks, add each as a new line.

```
  #checkov:skip=CKV_AWS_52
  #checkov:skip=CKV_AWS_20:The bucket is a public static content host
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

#### VSCODE Extension

If you want to use checkov's within vscode, give a try to the vscode extension availble at [vscode](https://marketplace.visualstudio.com/items?itemName=Bridgecrew.checkov)

## Alternatives

For Terraform compliance scanners check out [tfsec](https://github.com/liamg/tfsec) and [Terraform AWS Secure Baseline](https://github.com/nozaq/terraform-aws-secure-baseline) for secured basline.

For CloudFormation scanning check out [cfripper](https://github.com/Skyscanner/cfripper/) and [cfn_nag](https://github.com/stelligent/cfn_nag).

For Kubernetes scanning check out [kube-scan](https://github.com/octarinesec/kube-scan) and [Polaris](https://github.com/FairwindsOps/polaris).

## Contributing

Contribution is welcomed! 

Start by reviewing the [contribution guidelines](CONTRIBUTING.md). After that, take a look at a [good first issue](https://github.com/bridgecrewio/checkov/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

Looking to contribute new checks? Learn how to write a new check (AKA policy) [here](docs/5.Contribution/New-Check.md).

## Disclaimer
`checkov` does not save, publish or share with anyone any identifiable customer information.  
No identifiable customer information is used to query Bridgecrew's publicly accessible guides.
`checkov` uses Bridgecrew's API to enrich the results with links to remediation guides.
To skip this API call use the flag `--no-guide`.

## Support

[Bridgecrew](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov) builds and maintains Checkov to make policy-as-code simple and accessible. 

Start with our [Documentation](https://bridgecrewio.github.io/checkov/) for quick tutorials and examples.

If you need direct support you can contact us at info@bridgecrew.io.
