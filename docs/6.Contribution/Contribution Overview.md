---
layout: default
published: true
title: Contribution Overview
order: 1
---

# Contribution Overview

Checkov users are encouraged to contribute their custom Policies to help increase our existing IaC coverage.
Our aim is to help close gaps in real-world hardening, assessments, auditing and forensics. In other words, we specifically encourage contribution of new Policies that you think should be globally accepted when provisioning and changing infrastructure.

The main aspects of contributing new Policies are:
  * Preparing the prerequisites
  * Creating and Testing the Custom Policy (either YAML or Python format)
  * Pull Request

## Prerequisites

### Installation

First, make sure you installed and configured Checkov correctly. If you are unsure, go back and read the [Installing Checkov documentation](../2.Basics/Installing%20Checkov.md).

Preferably by now you have either scanned a folder containing Terraform state-files or went ahead and integrated Checkov as part of your CI/CD pipeline.

### Custom Policy Structure

Each check consists of the following mandatory properties:

**name:** A new Custom Policy's unique purpose. It should ideally specify the positive desired outcome of the policy.

**ID:** A mandatory unique identifier of a policy. Policies written by Checkov maintainers follow the following convention: **CKV_providerType_serialNumber**. (e.g., CKV_AWS_9 , CKV_GCP_12)

**Categories:** A categorization of a scan. This is usually helpful when producing compliance reports, pipeline analytics and health metrics. Check out our existing categories before creating a new one.

When contributing a Custom Policy, please increment the ID number to be x+1, where x is the serial number of the latest implemented Custom Policy, with respect to its provider (e.g., AWS).

A more specific type of Custom Policy may also include additional attributes. For example, a check that scans a Terraform resource configuration also contains the supported_resources attribute, which is a list of the supported resource types of the check.


### Result

The result of a scan should be a binary result of either PASSED or FAILED. We have also included an UNKNOWN option, which means that it is unknown if the scanned configuration complied with the check. If your check could have edge cases that might not be supported by the scanner’s current logic, consider support the UNKNOWN option.

Additionally, a Policy can be suppressed by Checkov on a given configuration by inserting a skip comment inside a specific configuration scope. Then, the result for that Policy would be SKIPPED.
For further details, see [Suppressions](../2.Basics/Suppressing%20and%20Skipping%20Policies.md).

### IaC Type Scanner

Identify which IaC type the check will test. Currently, Checkov can scan either Terraform or CloudFormation configuration files.
Place your code in the `checkov/<scanner>` folder, where `<scanner>` is either `terraform` or `cloudformation`.

Identify which IaC type will be tested under the Custom Policy. Currently, Checkov scans either Terraform or CloudFormation configuration files. Place your code in the `checkov/<scanner>` folder, where `<scanner>` is either terraform or cloudformation.

### Custom Policy Type and Provider

Custom Policies are divided first into folders grouped by type, and then grouped by provider.

Custom Policies should relate to a common IaC configuration type of a specific public cloud provider. For example, a Custom Policy that validates the encryption configuration of an S3 bucket is considered to be of type `resource`, and of `aws` provider.

Identify the type and provider of the new Custom Policy in order to place it correctly under the project structure. For example, the mentioned above check is already implemented in Checkov under `checkov/terraform/checks/resource/aws/S3Encryption.py`.

Notice that Custom Policies are divided into folders grouped by type, and then grouped provider.

### Review IaC Configuration Documentation

If available, please provide the official Terraform or CloudFormation documentation of the checked configuration. This helps users to better understand the Custom Policy's scanned configuration and usage.

For example, the documentation for the Custom Policy mentioned above is [here](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket).

### Sample IaC Configuration

In order to develop the Custom Policy, a relevant example configuration should be presented as an input to Checkov. Provide a sample configuration (e.g., `example.tf`, `template.json`) that contains both passing and failing configurations with respect to the Custom Policy's logic. The file can be served as an input to the appropriate Custom Policy's unit tests.

## Creating and Testing the Custom Policy
  * See [Create Python Policies](../3.Custom%20Policies/Create%20Python%20Policies.md) and [Contribute Python-Based Policies](../6.Contribution/Contribute%20Python-Based%20Policies.md).
  * See [Create YAML Policies](../3.Custom%20Policies/Create%20Python%20Policies.md) and [Contribute YAML-Based Policies](../6.Contribution/Contribute%20YAML-Based%20Policies.md).

## Pull Request
Open a PR that contains the implementation code and testing suite, with the following information:

  * Custom Policy `id`.
  * Custom Policy `name`.
  * Custom Policy IaC type.
  * Custom Policy type and provider.
  * IaC configuration documentation (If available).
  * Sample Terraform configuration file.
  * Any additional information that would help other members to better understand the check.

## Implementation

After identifying the check's IaC type and provider, place the file containing its code inside the folder `checkov/<scanner>/checks/<type>/<provider>`, where `<type>` is the check's type and `<provider>` is the check's provider.

A check is a class that implements an `abstract` base check class that corresponds to a particular provider and type.
For example, all checks with the type `resource` and the provider `aws` implement the resource base check class found at `checkov/terraform/checks/resource/base_check.py`. The resource check needs to implement the abstract method of its base check, named `scan_resource_conf`. The input for this is a dictionary of all the key-valued resource attributes, and the output is a `CheckResult`.

For an example of a full implementation of a check, please refer to the [Custom Policy Documentation](../3.Custom%Policies/Overview.md).

## Testing

To test the check, create an appropriate unit test file. Assuming the class file for your check is located in the directory `checkov/terraform/checks/<type>/<provider>`, and is named `<ClassName>.py`, you would the unit test file in the directory `tests/terraform/checks/<type>/<provider>` , and name it `test_<ClassName>.py`.

The test suite should cover different check results; Test if the check outputs `PASSED` on a compliant configuration, and test if it outputs `FAILED` on a non-compliant configuration. You are also encouraged to test more specific components of the check, according to their complexity.
