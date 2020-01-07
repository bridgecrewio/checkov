# Contribute a new check

Checkov contributors are more than welcomed to contribute new checks. With more implemented checks, Checkov's ability to
detect various security and compliance misconfigurations improves. 

This guide covers all the necessary steps required for contributing a new check.

## Prerequisites
### Installation
Make sure you have installed and configured Checkov correctly, by reading the [Getting Started](../1.Introduction/Getting%20Started.md)
page.
It is encouraged to run Checkov in order to get familiar with it's functionality.
 
### Check type and provider
Checkov's check should relate to a common Terraform configuration type of certain provider. 
For example, a check that validates the encryption configuration of an S3 bucket is considered to be of type `resource`,
and of `aws` provider. 

Identify the type and provider of the new check in order to place it correctly under the project structure.
For example, the mentioned above check is already implemented in Checkov under `checkov/terraform/checks/resource/aws/S3Encryption.py`.

As seen, checks are divided first to folders grouped by their type, and are after divided by their provider.

### Check's Terraform configuration documentation

If available, please provide the official [Terraform](https://www.terraform.io/docs) documentation of the checked 
configuration. 

For example, the mentioned above check's configuration documentation can be found [here](https://www.terraform.io/docs/providers/aws/r/s3_bucket.html) 

### Example Terraform configuration
In order to develop the check, a relevant example configuration should be presented as an input to Checkov.
Provide an example configuration (`example.tf`) that contains both `Passed` and `Failed` configurations with respect to 
the check's logic.
The file will serve as an input to the appropriate check's unit tests. 

## Implementation
