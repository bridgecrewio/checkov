---
layout: default
published: true
title: Contribute New Policy
order: 3
---
Checkov users are encouraged to contribute their custom checks, or *Policies* to help increase our existing IaC coverage.
Our aim is to help close gaps in real-world hardening, assessments, auditing and forensics. In other words, a new check should reflect a policy you think should be globally accepted when provisioning and changing infrastructure.

The main steps in contributing new Policies are:

1. Implementation
2. Testing
3. Pull Request

## Scripted Guide

### Contribution Stages

1. Prerequisites
    * Install Checkov as described in the [Installation](#installation) subsection.
    * Read about the structure and functionality of checks in the [Prerequisites](#prerequisites) section.
    * Identify the `type` and `provider` of the check, as described [here](#check-structure).
    * If available, provide the IaC configuration documentation that relates to the check, as described [here](#review-iac-configuration-documentation).
    * Provide an example Terraform or CloudFormation configuration file, as described [here](#example-Terraform-configuration).
2. Implementation
    * Implement the check as described in the [Implementation](#implementation) section.
3. Testing
    * Provide a unit test suite of the check as described in the [Testing](#testing) section.
4. Pull Request
    * Open a PR that contains the implementation code and testing suite, with the following information:
        * Check `id`.
        * Check `name`.
        * The check's IaC type.
        * Check type and provider.
        * IaC configuration documentation (If available).
        * Example Terraform configuration file.
        * Any additional information that would help other members to better understand the check.

## Prerequisites

### Installation

First, make sure you have correctly installed and configured Checkov. If you are unsure, go back and reread [Installing Checkov](doc:installing-checkov).
By now you should have either scanned a folder containing Terraform state-files or integrated Checkov as part of your CI/CD pipeline.

### Check Structure

Each check includes the following mandatory properties:
[block:parameters]
{
  "data": {
    "h-0": "Property",
    "h-1": "Description",
    "h-2": "Example/Comments",
    "0-0": "``name``",
    "0-1": "The unique purpose of a new check. It should ideally specify the positive desired outcome of the policy.",
    "1-0": "``id``",
    "1-1": "A mandatory unique identifier of a policy.\nPolicies written by Checkov maintainers follow the following convention ``CKV_providerType_serialNumber``.",
    "1-2": "`CKV_AWS_9`\n`CKV_GCP_12`",
    "2-0": "``categories``",
    "2-1": "A categorization of a scan.",
    "2-2": "This is usually helpful when producing compliance reports, pipeline analytics and health metrics. \nCheck out our existing categories before creating a new one."
  },
  "cols": 3,
  "rows": 3
}
[/block]
When contributing a new check, the `id`'s serial number should rise incrementally as `x+1`, where `x` is the serial number of the latest check implemented by that provider.
More specific types of check may also include additional attributes. For example, a check that scans a Terraform resource configuration also contains the `supported_resources` attribute, which is a list of the supported resource types of the check.

### Check Result

The result of a scan should be a binary result of either `PASSED` or `FAILED`. We have also included an `UNKNOWN` option, which means that it is unknown if the scanned configuration complied with the check. If your check could have edge cases that might not be supported by the scanner's current logic, consider supporting the `UNKNOWN` option.
Additionally, a check can be suppressed by Checkov on a given configuration by inserting a skip comment inside a specific configuration scope. Then, the check's result on the suppressed configuration would be `SKIPPED`.
Read more about Checkov's [Suppressions](doc:suppress) for further details.

## IaC Type Scanner

Identify which IaC type the check will test. Currently, Checkov can scan either Terraform or CloudFormation configuration files.
Place your code in the `checkov/<scanner>` folder, where `<scanner>` is either `terraform` or `cloudformation`.

### Check Type and Provider

Checks are initially divided into folders grouped by type, and then by provider.
Checks should relate to a common IaC configuration type of a specific public cloud provider. For example, a check that validates the encryption configuration of an S3 bucket is considered to be of the type `resource`, and of the provider `aws`.

Identify the type and provider of the new check to ensure it is correctly placed in the project structure. For example, the above-mentioned check is already implemented in Checkov under `checkov/terraform/checks/resource/aws/S3Encryption.py`.
Note again that checks are divided into folders grouped first by type, and then by provider.

### Review IaC Configuration Documentation

If available, please provide the official [Terraform](https://www.terraform.io/docs) or [CloudFormation](https://docs.aws.amazon.com/cloudformation/) documentation of the checked configuration. This makes it easier for users to understand the scanned configuration of the check, and how to use it.
For example, the configuration documentation for the check described above can be found [here](https://www.terraform.io/docs/providers/aws/r/s3_bucket.html).

### Example IaC Configuration

In order to develop the check, present a relevant example configuration (e.g. `example.tf, template.json`) as an input to Checkov. The example should include configurations that both pass and fail according to the check's logic. You can serve the file as an input to the appropriate check's unit tests.

## Implementation

After identifying the check's IaC type and provider, place the file containing its code inside the folder `checkov/<scanner>/checks/<type>/<provider>`, where `<type>` is the check's type and `<provider>` is the check's provider.

A check is a class that implements an `abstract` base check class that corresponds to a particular provider and type.
For example, all checks with the type `resource` and the provider `aws` implement the resource base check class found at `checkov/terraform/checks/resource/base_check.py`. The resource check needs to implement the abstract method of its base check, named `scan_resource_conf`. The input for this is a dictionary of all the key-valued resource attributes, and the output is a `CheckResult`.

For an example of a full implementation of a check, please refer to the [Policy Documentation](doc:custom-policies).

## Testing

To test the check, create an appropriate unit test file. Assuming the class file for your check is located in the directory `checkov/terraform/checks/<type>/<provider>`, and is named `<ClassName>.py`, you would the unit test file in the directory `tests/terraform/checks/<type>/<provider>` , and name it `test_<ClassName>.py`.

The test suite should cover different check results; Test if the check outputs `PASSED` on a compliant configuration, and test if it outputs `FAILED` on a non-compliant configuration. You are also encouraged to test more specific components of the check, according to their complexity.
