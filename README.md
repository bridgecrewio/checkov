[![checkov](https://raw.githubusercontent.com/bridgecrewio/checkov/master/docs/web/images/checkov_by_bridgecrew.png)](#)
       
[![Maintained by Bridgecrew.io](https://img.shields.io/badge/maintained%20by-bridgecrew.io-blueviolet)](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![build status](https://github.com/bridgecrewio/checkov/workflows/build/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Abuild)
[![security status](https://github.com/bridgecrewio/checkov/workflows/security/badge.svg)](https://github.com/bridgecrewio/checkov/actions?query=event%3Apush+branch%3Amaster+workflow%3Asecurity) 
[![code_coverage](https://raw.githubusercontent.com/bridgecrewio/checkov/master/coverage.svg?sanitize=true)](https://github.com/bridgecrewio/checkov/actions?query=workflow%3Acoverage) 
[![docs](https://img.shields.io/badge/docs-passing-brightgreen)](https://www.checkov.io/1.Welcome/What%20is%20Checkov.html?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov)
[![PyPI](https://img.shields.io/pypi/v/checkov)](https://pypi.org/project/checkov/)
[![Python Version](https://img.shields.io/pypi/pyversions/checkov)](#)
[![Terraform Version](https://img.shields.io/badge/tf-%3E%3D0.12.0-blue.svg)](#)
[![Downloads](https://pepy.tech/badge/checkov)](https://pepy.tech/project/checkov)
[![Docker Pulls](https://img.shields.io/docker/pulls/bridgecrew/checkov.svg)](https://hub.docker.com/r/bridgecrew/checkov)
[![slack-community](https://img.shields.io/badge/Slack-4A154B?style=plastic&logo=slack&logoColor=white)](https://slack.bridgecrew.io/)
 

**Checkov** is a static code analysis tool for infrastructure as code (IaC) and also a software composition analysis (SCA) tool for images and open source packages.

It scans cloud infrastructure provisioned using [Terraform](https://terraform.io/), [Terraform plan](docs/7.Scan%20Examples/Terraform%20Plan%20Scanning.md), [Cloudformation](docs/7.Scan%20Examples/Cloudformation.md), [AWS SAM](docs/7.Scan%20Examples/AWS%20SAM.md), [Kubernetes](docs/7.Scan%20Examples/Kubernetes.md), [Helm charts](docs/7.Scan%20Examples/Helm.md), [Kustomize](docs/7.Scan%20Examples/Kustomize.md), [Dockerfile](docs/7.Scan%20Examples/Dockerfile.md),  [Serverless](docs/7.Scan%20Examples/Serverless%20Framework.md), [Bicep](docs/7.Scan%20Examples/Bicep.md), [OpenAPI](docs/7.Scan%20Examples/OpenAPI.md) or [ARM Templates](docs/7.Scan%20Examples/Azure%20ARM%20templates.md) and detects security and compliance misconfigurations using graph-based scanning.

It performs [Software Composition Analysis (SCA) scanning](docs/7.Scan%20Examples/Sca.md) which is a scan of open source packages and images for Common Vulnerabilities and Exposures (CVEs).
 
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
 * Scans Terraform, Terraform Plan, CloudFormation, AWS SAM, Kubernetes, Dockerfile, Serverless framework, Ansible, Bicep and ARM template files.
 * Scans Argo Workflows, Azure Pipelines, BitBucket Pipelines, Circle CI Pipelines, GitHub Actions and GitLab CI workflow files
 * Supports Context-awareness policies based on in-memory graph-based scanning.
 * Supports Python format for attribute policies and YAML format for both attribute and composite policies.
 * Detects [AWS credentials](docs/2.Basics/Scanning%20Credentials%20and%20Secrets.md) in EC2 Userdata, Lambda environment variables and Terraform providers.
 * [Identifies secrets](https://bridgecrew.io/blog/checkov-secrets-scanning-find-exposed-credentials-in-iac/) using regular expressions, keywords, and entropy based detection.
 * Evaluates [Terraform Provider](https://registry.terraform.io/browse/providers) settings to regulate the creation, management, and updates of IaaS, PaaS or SaaS managed through Terraform.
 * Policies support evaluation of [variables](docs/2.Basics/Handling%20Variables.md) to their optional default value.
 * Supports in-line [suppression](docs/2.Basics/Suppressing%20and%20Skipping%20Policies.md) of accepted risks or false-positives to reduce recurring scan failures. Also supports global skip from using CLI.
 * [Output](docs/2.Basics/Reviewing%20Scan%20Results.md) currently available as CLI, [CycloneDX](https://cyclonedx.org), JSON, JUnit XML, CSV, SARIF and github markdown and link to remediation [guides](https://docs.bridgecrew.io/docs/aws-policy-index).
 
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

or using [homebrew](https://formulae.brew.sh/formula/checkov) (macOS or Linux)

```sh
brew install checkov
```

or

```sh
brew upgrade checkov
```

### Enabling bash autocomplete
```sh
source <(register-python-argcomplete checkov)
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
Note: `terraform show` output file `tf.json` will be a single line. 
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

Alternatively, specify the repo root of the hcl files used to generate the plan file, using the `--repo-root-for-plan-enrichment` flag, to enrich the output with the appropriate file path, line numbers, and codeblock of the resource(s). An added benefit is that check suppressions will be handled accordingly.
```sh
checkov -f tf.json --repo-root-for-plan-enrichment /user/path/to/iac/code
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

Start using Checkov by reading the [Getting Started](docs/1.Welcome/Quick%20Start.md) page.

### Using Docker


```sh
docker pull bridgecrew/checkov
docker run --tty --rm --volume /user/tf:/tf --workdir /tf bridgecrew/checkov --directory /tf
```
Note: if you are using Python 3.6(Default version in Ubuntu 18.04) checkov will not work and it will fail with `ModuleNotFoundError: No module named 'dataclasses'`  error message. In this case, you can use the docker version instead.

Note that there are certain cases where redirecting `docker run --tty` output to a file - for example, if you want to save the Checkov JUnit output to a file - will cause extra control characters to be printed. This can break file parsing. If you encounter this, remove the `--tty` flag.

The `--workdir /tf` flag is optional to change the working directory to the mounted volume. If you are using the SARIF output `-o sarif` this will output the results.sarif file to the mounted volume (`/user/tf` in the example above). If you do not include that flag, the working directory will be "/".

### Running or skipping checks 

By using command line flags, you can specify to run only named checks (allow list) or run all checks except 
those listed (deny list). If you are using the platform integration via API key, you can also specify a severity threshold to skip and / or include.
Moreover, as json files can't contain comments, one can pass regex pattern to skip json file secret scan.

See the docs for more detailed information about how these flags work together.
   

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

Run a scan of a container image. First pull or build the image then refer to it by the hash, ID, or name:tag:
```sh
checkov --framework sca_image --docker-image sha256:1234example --dockerfile-path /Users/path/to/Dockerfile --bc-api-key ...

checkov --docker-image <image-name>:tag --dockerfile-path /User/path/to/Dockerfile --bc-api-key ...
```

You can use --image flag also to scan container image instead of --docker-image for shortener:
```sh
checkov --image <image-name>:tag --dockerfile-path /User/path/to/Dockerfile --bc-api-key ...
```

Run an SCA scan of packages in a repo:
```sh
checkov -d . --framework sca_package --bc-api-key ... --repo-id <repo_id(arbitrary)>
```

Run a scan of a directory with environment variables removing buffering, adding debug level logs, turning on image referencer:
```sh
PYTHONUNBUFFERED=1 LOG_LEVEL=DEBUG CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING=TRUE checkov -d .
```
OR enable the environment variables for multiple runs
```sh
export PYTHONUNBUFFERED=1 LOG_LEVEL=DEBUG CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING=TRUE
checkov -d .
```

Run secrets scanning on all files in MyDirectory. Skip CKV_SECRET_6 check on json files that their suffix is DontScan
```sh
checkov -d /MyDirectory --framework secrets --bc-api-key ... --skip-check CKV_SECRET_6:.*DontScan.json$
```

Run secrets scanning on all files in MyDirectory. Skip CKV_SECRET_6 check on json files that contains "skip_test" in path
```sh
checkov -d /MyDirectory --framework secrets --bc-api-key ... --skip-check CKV_SECRET_6:.*skip_test.*json$
```

One can mask values from scanning results by supplying a configuration file (using --config-file flag) with mask entry.
The masking can apply on resource & value (or multiple values, seperated with a comma). 
Examples:
```sh
mask:
- aws_instance:user_data
- azurerm_key_vault_secret:admin_password,user_passwords
```
In the example above, the following values will be masked:
- user_data for aws_instance resource
- both admin_password &user_passwords for azurerm_key_vault_secret


### Suppressing/Ignoring a check

Like any static-analysis tool it is limited by its analysis scope. 
For example, if a resource is managed manually, or using subsequent configuration management tooling, 
suppression can be inserted as a simple code annotation.

#### Suppression comment format

To skip a check on a given Terraform definition block or CloudFormation resource, apply the following comment pattern inside it's scope:

`checkov:skip=<check_id>:<suppression_comment>`

* `<check_id>` is one of the [available check scanners](docs/5.Policy Index/all.md)
* `<suppression_comment>` is an optional suppression reason to be included in the output

#### Example

The following comment skips the `CKV_AWS_20` check on the resource identified by `foo-bucket`, where the scan checks if an AWS S3 bucket is private.
In the example, the bucket is configured with public read access; Adding the suppress comment would skip the appropriate check instead of the check to fail.

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
  #checkov:skip=CKV2_AWS_6
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

For detailed logging to stdout set up the environment variable `LOG_LEVEL` to `DEBUG`. 

Default is `LOG_LEVEL=WARNING`.

#### Skipping directories
To skip files or directories, use the argument `--skip-path`, which can be specified multiple times. This argument accepts regular expressions for paths relative to the current working directory. You can use it to skip entire directories and / or specific files.

By default, all directories named `node_modules`, `.terraform`, and `.serverless` will be skipped, in addition to any files or directories beginning with `.`.
To cancel skipping directories beginning with `.` override `CKV_IGNORE_HIDDEN_DIRECTORIES` environment variable `export CKV_IGNORE_HIDDEN_DIRECTORIES=false`

You can override the default set of directories to skip by setting the environment variable `CKV_IGNORED_DIRECTORIES`.
 Note that if you want to preserve this list and add to it, you must include these values. For example, `CKV_IGNORED_DIRECTORIES=mynewdir` will skip only that directory, but not the others mentioned above. This variable is legacy functionality; we recommend using the `--skip-file` flag.

#### Console Output

The console output is in colour by default, to switch to a monochrome output, set the environment variable:
`ANSI_COLORS_DISABLED`

#### VSCODE Extension

If you want to use checkov's within vscode, give a try to the vscode extension available at [vscode](https://marketplace.visualstudio.com/items?itemName=Bridgecrew.checkov)

### Configuration using a config file

Checkov can be configured using a YAML configuration file. By default, checkov looks for a `.checkov.yaml` or `.checkov.yml` file in the following places in order of precedence:
* Directory against which checkov is run. (`--directory`)
* Current working directory where checkov is called.
* User's home directory.

**Attention**: it is a best practice for checkov configuration file to be loaded from a trusted source composed by a verified identity, so that scanned files, check ids and loaded custom checks are as desired.

Users can also pass in the path to a config file via the command line. In this case, the other config files will be ignored. For example:
```sh
checkov --config-file path/to/config.yaml
```
Users can also create a config file using the `--create-config` command, which takes the current command line args and writes them out to a given path. For example:
```sh
checkov --compact --directory test-dir --docker-image sample-image --dockerfile-path Dockerfile --download-external-modules True --external-checks-dir sample-dir --no-guide --quiet --repo-id bridgecrew/sample-repo --skip-check CKV_DOCKER_3,CKV_DOCKER_2 --skip-fixes --skip-framework dockerfile secrets --skip-suppressions --soft-fail --branch develop --check CKV_DOCKER_1 --create-config /Users/sample/config.yml
```
Will create a `config.yaml` file which looks like this:
```yaml
branch: develop
check:
  - CKV_DOCKER_1
compact: true
directory:
  - test-dir
docker-image: sample-image
dockerfile-path: Dockerfile
download-external-modules: true 
evaluate-variables: true 
external-checks-dir: 
  - sample-dir 
external-modules-download-path: .external_modules 
framework:
  - all 
no-guide: true 
output: cli 
quiet: true 
repo-id: bridgecrew/sample-repo 
skip-check: 
  - CKV_DOCKER_3 
  - CKV_DOCKER_2 
skip-fixes: true 
skip-framework:
  - dockerfile
  - secrets
skip-suppressions: true 
soft-fail: true
```

Users can also use the `--show-config` flag to view all the args and settings and where they came from i.e. commandline, config file, environment variable or default. For example:
```sh
checkov --show-config
```
Will display:
```sh
Command Line Args:   --show-config
Environment Variables:
  BC_API_KEY:        your-api-key
Config File (/Users/sample/.checkov.yml):
  soft-fail:         False
  branch:            master
  skip-check:        ['CKV_DOCKER_3', 'CKV_DOCKER_2']
Defaults:
  --output:          cli
  --framework:       ['all']
  --download-external-modules:False
  --external-modules-download-path:.external_modules
  --evaluate-variables:True
```
## Contributing

Contribution is welcomed! 

Start by reviewing the [contribution guidelines](CONTRIBUTING.md). After that, take a look at a [good first issue](https://github.com/bridgecrewio/checkov/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

You can even start this with one-click dev in your browser through Gitpod at the following link:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/bridgecrewio/checkov)

Looking to contribute new checks? Learn how to write a new check (AKA policy) [here](docs/6.Contribution/Contribution%20Overview.md).

## Disclaimer
`checkov` does not save, publish or share with anyone any identifiable customer information.  
No identifiable customer information is used to query Bridgecrew's publicly accessible guides.
`checkov` uses Bridgecrew's API to enrich the results with links to remediation guides.
To skip this API call use the flag `--no-guide`.

## Support

[Bridgecrew](https://bridgecrew.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov) builds and maintains Checkov to make policy-as-code simple and accessible. 

Start with our [Documentation](https://bridgecrewio.github.io/checkov/) for quick tutorials and examples.

If you need direct support you can contact us at info@bridgecrew.io.

## Python Version Support
We follow the official support cycle of Python and we use automated tests for all supported versions of Python. This means we currently support Python 3.7 - 3.11, inclusive. Note that Python 3.7 is reaching EOL on June 2023. After that time, we will have a short grace period where we will continue 3.7 support until September 2023, and then it will no longer be considered supported for Checkov. If you run into any issues with any non-EOL Python version, please open an Issue.
