---
layout: default
published: true
title: Installing Checkov
nav_order: 1
---
Installing Checkov is quick and straightforward—just install, configure input, and scan.

### Install From PyPI Using Pip

```shell
pip install checkov
```

### Install on Python

```shell
pip3 install checkov
```

### Install on Alpine

```shell
pip3 install --upgrade pip && pip3 install --upgrade setuptools
pip3 install checkov
```

### Install on Ubuntu 18.04 LTS

Ubuntu 18.04 ships with Python 3.6. Before you can install Checkov, you need to install python 3.7 (from the PPA repository):

```shell
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
sudo apt install python3-pip
sudo python3.7 -m pip install -U checkov #to install or upgrade checkov)
```

or using homebrew (MacOS only)

```shell
brew install checkov
or

brew upgrade checkov
```

## Upgrading Checkov

If you installed Checkov with pip3, use the following command to upgrade:

```shell
pip3 install -U checkov
```

## Configure an input folder or file

### Configure a folder

```shell
checkov --directory /user/path/to/iac/code
```

### Configure a specific file

```shell
checkov --file /user/tf/example.tf
```

### Configure Multiple Specific Files

```shell
checkov -f /user/cloudformation/example1.yml -f /user/cloudformation/example2.yml
```

### Configure a Terraform Plan file in JSON

```json
terraform init
terraform plan -out tf.plan
terraform show -json tf.plan  > tf.json 
checkov -f tf.json
```

Note: The Terraform show output file `tf.json` will be a single line. For that reason Checkov will report all findings as line number 0.

```json
check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enabled"
	FAILED for resource: aws_s3_bucket.customer
	File: /tf/tf.json:0-0
	Guide: https://docs.bridgecrew.io/docs/s3_16-enable-versioning
```

If you have installed jq, you can convert a JSON file into multiple lines with the command `terraform show -json tf.plan | jq '.' > tf.json`, making it easier to read the scan result.

```json
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
