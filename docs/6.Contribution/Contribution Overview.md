---
layout: default
published: true
title: Contribution Overview
nav_order: 1
---

# Contribution Overview

Checkov users are encouraged to contribute their custom Policies to help increase our existing IaC coverage.
Our aim is to help close gaps in real-world hardening, assessments, auditing and forensics. In other words, we specifically encourage contribution of new Policies that you think should be globally accepted when provisioning and changing infrastructure.

The main aspects of contributing new Policies are:
  * Preparing the prerequisites
  * Creating and Testing the Custom Policy (either YAML or Python format)
  * Pull Request

## Prerequisites

### Video guide

<div align="left">
      <a href="https://www.youtube.com/watch?v=62F1-50g9D4">
         <img src="https://img.youtube.com/vi/62F1-50g9D4/0.jpg" style="width:100%;">
      </a>
</div>

### Installation

First, make sure you installed and configured Checkov correctly. If you are unsure, go back and read the [Installing Checkov documentation](https://www.checkov.io/2.Basics/Installing%20Checkov.html).

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
For further details, see [Suppressions](https://www.checkov.io/2.Basics/Suppressing%20and%20Skipping%20Policies.html).

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

For example, the documentation for the Custom Policy mentioned above is [here](https://www.checkov.io/3.Custom%20Policies/Custom%20Policies%20Overview.html).

### Sample IaC Configuration

In order to develop the Custom Policy, a relevant example configuration should be presented as an input to Checkov. Provide a sample configuration (e.g., `example.tf`, `template.json`) that contains both passing and failing configurations with respect to the Custom Policy's logic. The file can be served as an input to the appropriate Custom Policy's unit tests.

## Creating and Testing the Custom Policy
  * See [Create Python Policies](https://www.checkov.io/3.Custom%20Policies/Python%20Custom%20Policies.html) and [Contribute Python-Based Policies](https://www.checkov.io/6.Contribution/Contribute%20Python-Based%20Policies.html).
  * See [Create YAML Policies](https://www.checkov.io/3.Custom%20Policies/YAML%20Custom%20Policies.html) and [Contribute YAML-Based Policies](https://www.checkov.io/6.Contribution/Contribute%20YAML-based%20Policies.html).

## Pull Request
Open a PR that contains the implementation code and testing suite, with the following information:

  * Custom Policy `id`.
  * Custom Policy `name`.
  * Custom Policy IaC type.
  * Custom Policy type and provider.
  * IaC configuration documentation (If available).
  * Sample Terraform configuration file.
  * Any additional information that would help other members to better understand the check.
