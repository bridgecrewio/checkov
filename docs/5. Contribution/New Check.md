# Contributing a new check

## Background

Checkov contributors are encouraged to contribute new checks to help increase our existing coverage of infrastructure-as-code. 

In our documentation, a check is sometimes referred loosely also as a Policy. We expect to solve a real-world hardening, assessment, auditing or forensic gap you encountered. In other words, a new check should reflect a policy you think should be globally accepted when provisioning and changing infrastructure.

This guide covers all the necessary stages required to building and contributing a new check, which are:

1. Prerequisites
2. Implementation
3. Testing
4. Pull Request

## Contribution Stages
1. Prerequisites
    * Install Checkov as described in the [Installation](#installation) subsection.
    * Read about check's structure and functionality in the [Prerequisites](#prerequisites) section.
    * Identify the check's `type` and `provider`, as described [here](#check-structure). 
    * If available, provide the IaC configuration documentation that relates to the check, as described [here](#review-iac-configuration-documentation).
    * Provide an example Terraform configuration file, as described [here](#example-Terraform-configuration). 
2. Implementation
    * Implement the check as described in the [Implementation](#implementation) section.
3. Testing
    * Provide a unit test suite of the check as described in the [Testing](#testing) section.
4. Pull Request
    * Open a PR that contains the implementing code and testing suite, with the following information:
        * Check `id`
        * Check `name`
        * Check type and provider
        * IaC configuration documentation (If available)
        * Example Terraform configuration file
        * Any additional information that would help other members to better understand the check

## Prerequisites

### Installation

First, make sure you installed and configured Checkov correctly. If you are unsure, go back and read the [Getting Started](../1.Introduction/Getting%20Started.md).

Preferably by now you have either scanned a folder containing Terraform state-files or went ahead and integrated Checkov as part of your CI/CD pipeline.

### Check structure

Each check consists of the following mandatory properties:

``name`` : A new check's unique purpose. It should ideally specify the positive desired outcome of the policy.

``id``: A mandatory unique identifier of a policy. Policies written by Checkov maintainers follow the following convention ``CKV_providerType_serialNumber``. (e.g. `CKV_AWS_9` , `CKV_GCP_12`)

``categories``: A categorization of a scan. This is usually helpful when producing compliance reports, pipeline analytics and health metrics. Check out our existing categories before creating a new one.

When contributing a new check, please increment the `id`'s serial number to be `x+1`, where `x` is the serial number of the latest implemented check, with respect to the check's provider.

A more specific type of check may also include additional attributes. For example, a check that scans a Terraform resource configuration also contains the `supported_resources` attribute, which is a list of the supported resource types of the check.

### Check result

The result of a scan should be a binary result of either `PASSED` or `FAILED`. We have also included an `UNKNOWN` option, which means that it is unknown if  the scanned configuration complied with the check. If your check could have edge cases that might not be supported by the scanner's current logic, consider support the  `UNKNOWN` option.

Additionally, a check can be suppressed by Checkov on a given configuration by inserting a skip comment inside a specific configuration scope. Then, the check's result on the suppressed configuration would be `SKIPPED`.      
Read more about Checkov's [Suppressions](../3.Scans/resource-scans.md) for further details.

### Check type and provider

Checks are divided first to folders grouped by their type, and are after divided by their provider.

Checks should relate to a common Terraform configuration type of a specific public cloud provider. 
For example, a check that validates the encryption configuration of an S3 bucket is considered to be of type `resource`, and of `aws` provider. 

Identify the type and provider of the new check in order to place it correctly under the project structure.
For example, the mentioned above check is already implemented in Checkov under `checkov/terraform/checks/resource/aws/S3Encryption.py`.

Notice that checks are divided first into folders grouped by their type, and are after that divided by their provider.

### Review IaC configuration documentation

If available, please provide the official [Terraform](https://www.terraform.io/docs) documentation of the checked configuration. This helps users to better understand the check's scanned configuration and it's usage.

For example, the mentioned above check's configuration documentation can be found [here](https://www.terraform.io/docs/providers/aws/r/s3_bucket.html) 

### Example Terraform configuration

In order to develop the check, a relevant example configuration should be presented as an input to Checkov.
Provide an example configuration (`example.tf`) that contains both passing and failing configurations with respect to 
the check's logic.
The file can be served as an input to the appropriate check's unit tests. 



## Implementation

After identifying the check's type and provider, place the file containing it's code inside `checkov/terraform/checks/<type>/<provider>`, where `<type>` is the check's type and `<provider>` is the check's provider.

A check is a class implementing an `abstract` base check class that corresponds to some provider and type. 

For example, all checks of `resource` type and `aws` provider are implementing the resource base check class found at 
`checkov/terraform/checks/resource/base_check.py`. The resource check needs to implement it's base check's abstract method named 
`scan_resource_conf`, which accepts as an input a dictionary of all the key-valued resource attributes, and outputs a `CheckResult`.

For a full implementation example of a check, please refer the [Policies documentation](../1.Introduction/Policies.md).

## Testing

Assuming the implemented check's class is file is found in `checkov/terraform/checks/<type>/<provider>` directory, named `<ClassName>.py`, create an appropriate unit test file in `tests/terraform/checks/<type>/<provider>` directory, named `test_<ClassName>.py`.

The test suite should cover different check results; Test if the check outputs `PASSED` on a compliant configuration,
and test if it output `FAILED` on a non-compliant configuration. You are also encouraged to test more specific 
components of the check, according to their complexity.

