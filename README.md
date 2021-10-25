[![Hacktoberfest](docs/web/images/Hacktoberfest-1.png)](https://bridgecrew.io/blog/happy-hacktoberfest-2021/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![checkov](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/web/images/checkov_by_bridgecrew.png)](#)
       
[![Maintained by Bridgecrew.io](https://img.shields.io/badge/maintained%20by-bridgecrew.io-blueviolet)](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![build status](https://github.com/bridgecrewio/checkov/workflows/build/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Abuild)
[![security status](https://github.com/bridgecrewio/checkov/workflows/security/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=event%3Apush+branch%3Amaster+workflow%3Asecurity) 
[![code_coverage](https://raw.githubusercontent.com/bridgecrewio/checkov/master/coverage.svg?sanitize=true)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Acoverage) 
[![docs](https://img.shields.io/badge/docs-passing-brightgreen)](https://www.checkov.io/1.Welcome/What%20is%20Checkov.html?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![PyPI](https://img.shields.io/pypi/v/checkov)](https://pypi.org/project/checkov/)
[![Python Version](https://img.shields.io/github/pipenv/locked/python-version/bridgecrewio/checkov)](#)
[![Terraform Version](https://img.shields.io/badge/tf-%3E%3D0.12.0-blue.svg)](#)
[![Downloads](https://pepy.tech/badge/checkov)](https://pepy.tech/project/checkov)
[![slack-community](https://img.shields.io/badge/Slack-4A154B?style=plastic&logo=slack&logoColor=white)](https://slack.bridgecrew.io/)
 
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
 * [Over 1000 built-in policies](docs/5.Policy%20Index/all.md) cover security and compliance best practices for AWS, Azure and Google Cloud.
 * Scans Terraform, Terraform Plan, CloudFormation, Kubernetes, Dockerfile, Serverless framework and ARM template files.
 * Supports Context-awareness policies based on in-memory graph-based scanning.
 * Supports Python format for attribute policies and YAML format for both attribute and composite policies.
 * Detects [AWS credentials](docs/2.Basics/Scanning%20Credentials%20and%20Secrets.md) in EC2 Userdata, Lambda environment variables and Terraform providers.
 * [Identifies secrets](https://bridgecrew.io/blog/checkov-secrets-scanning-find-exposed-credentials-in-iac/) using regular expressions, keywords, and entropy based detection.
 * Evaluates [Terraform Provider](https://registry.terraform.io/browse/providers) settings to regulate the creation, management, and updates of IaaS, PaaS or SaaS managed through Terraform.
 * Policies support evaluation of [variables](docs/2.Basics/Handling%20Variables.md) to their optional default value.
 * Supports in-line [suppression](docs/2.Basics/Suppressing%20and%20Skipping%20Policies.md) of accepted risks or false-positives to reduce recurring scan failures. Also supports global skip from using CLI.
* [Output](docs/2.Basics/Reviewing%20Scan%20Results.md) currently available as CLI, JSON, JUnit XML and github markdown and link to remediation [guides](https://docs.bridgecrew.io/docs/aws-policy-index).
 
## Screenshots
Scan results in CLI
![scan-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/checkov-recording.gif)
Scheduled scan result in Jenkins
![jenikins-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/checkov-jenkins.png)
## Getting started
### Requirements
  * Python >= 3.7 (Data classes are available for Python 3.7+)
  * Terraform >= 0.12

 ### Installation
 ### Installation:


 ```sh
 @@ -81,7 +81,7 @@ pip3 install checkov

 Installation on Ubuntu 18.04 LTS:

 Ubuntu 18.04 ships with Python 3.6. Install python 3.7 (from ppa repository)
 Ubuntu 18.04 ships with Python 3.6. [Install python 3.7 (from ppa repository)]

 ```sh
 sudo apt update
 @@ -92,7 +92,7 @@ sudo apt install python3-pip
 sudo python3.7 -m pip install -U checkov #to install or upgrade checkov)
 ```

 or using homebrew (MacOS only)
 or using Homebrew (MacOS only)

 ```sh
 brew install checkov
 @@ -104,30 +104,30 @@ or
 brew upgrade checkov
 ```

 ### Upgrade
 ### Upgrade:

 if you installed checkov with pip3
 ```sh
 pip3 install -U checkov
 ```

 ### Configure an input folder or file
 ### Configure an input folder or file:

 ```sh
 checkov --directory /user/path/to/iac/code
 ```

 Or a specific file or files
 Or a specific file or files:

 ```sh
 checkov --file /user/tf/example.tf
 ```
 Or
 Or,
 ```sh
 checkov -f /user/cloudformation/example1.yml -f /user/cloudformation/example2.yml
 ```

 Or a terraform plan file in json format
 Or a terraform plan file in json format:
 ```sh
 terraform init
 terraform plan -out tf.plan
 @@ -143,7 +143,7 @@ check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enab
 	Guide: https://docs.bridgecrew.io/docs/s3_16-enable-versioning
   ```

 If you have installed `jq` you can convert json file into multiple lines with the following command:
 If you have installed `jq` you can convert the json file into multiple lines with the following command:
 ```sh
 terraform show -json tf.plan | jq '.' > tf.json 
 ```
 @@ -162,7 +162,7 @@ Check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enab

 ```

 Alternatively, specify the repo root of the hcl files used to generate the plan file, using the `--repo-root-for-plan-enrichment` flag, to enrich the output with the appropriate file path, line numbers, and codeblock of the resource(s). An added benefit is that check suppressions will be handled accordingly.
 Alternatively, specify the repo root of the hcl files is being used to generate the plan file, using the `--repo-root-for-plan-enrichment` flag, to enrich the output with the appropriate file path, line numbers, and codeblock of the resource(s). An added benefit would be that check suppressions will be handled accordingly.
 ```sh
 checkov -f tf.json --repo-root-for-plan-enrichment /user/path/to/iac/code
 ```
 @@ -191,11 +191,11 @@ docker run --tty --volume /user/tf:/tf bridgecrew/checkov --directory /tf
 ```
 Note: if you are using Python 3.6(Default version in Ubuntu 18.04) checkov will not work and it will fail with `ModuleNotFoundError: No module named 'dataclasses'`  error message. In this case, you can use the docker version instead.

 Note that there are certain cases where redirecting `docker run --tty` output to a file - for example, if you want to save the Checkov JUnit output to a file - will cause extra control characters to be printed. This can break file parsing. If you encounter this, remove the `--tty` flag.
 Note that there are certain cases where redirecting `docker run --tty` output to a file - for example, if you want to save the Checkov JUnit output to a file - shall cause extra control characters to be printed. This could break file parsing. If you encounter this, kindly remove the `--tty` flag.

 ### Running or skipping checks 

 Using command line flags you can specify to run only named checks (allow list) or run all checks except 
 Using command line flags that you can specify to run only named checks (allow list) or run all checks except 
 those listed (deny list).

 List available checks:
 @@ -299,13 +299,13 @@ For detailed logging to stdout setup the environment variable `LOG_LEVEL` to `DE
 Default is `LOG_LEVEL=WARNING`.

 #### Skipping directories
 To skip files or directories, use the argument `--skip-path`, which can be specified multiple times. This argument accepts regular expressions for paths relative to the current working directory. You can use it to skip entire directories and / or specific files.
 To skip files or directories, the argument `--skip-path`, can be used, which can be specified multiple times. This argument accepts regular expressions for paths relative to the current working directory. You can use it to skip entire directories and / or specific files.

 By default, all directories named `node_modules`, `.terraform`, and `.serverless` will be skipped, in addition to any files or directories beginning with `.`.
 To cancel skipping directories beginning with `.` override `IGNORE_HIDDEN_DIRECTORY_ENV` environment variable `export IGNORE_HIDDEN_DIRECTORY_ENV=false`

 You can override the default set of directories to skip by setting the environment variable `CKV_IGNORED_DIRECTORIES`.
  Note that if you want to preserve this list and add to it, you must include these values. For example, `CKV_IGNORED_DIRECTORIES=mynewdir` will skip only that directory, but not the others mentioned above. This variable is legacy functionality; we recommend using the `--skip-file` flag.
  Please note that if you want to preserve this list and add to it, you must include these values. For example, `CKV_IGNORED_DIRECTORIES=mynewdir` will skip only that directory, but not the others mentioned above. This variable is legacy functionality; we recommend using the `--skip-file` flag.

 #### VSCODE Extension
