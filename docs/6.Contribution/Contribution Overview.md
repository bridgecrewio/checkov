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

### Installation

First, make sure you installed and configured Checkov correctly. If you are unsure, go back and read the [Installing Checkov documentation](https://www.checkov.io/2.Basics/Installing%20Checkov.html).

Preferably by now you have either scanned a folder containing Terraform state-files or went ahead and integrated Checkov as part of your CI/CD pipeline.

### Add A Check via CLI Prompt
Let's assume we're trying to create a new AWS resource Check to ensure all of our `aws_iam_policy`'s have a tag that says `{ "Checkov" = "IsAwesome" }`

1. Run `checkov --add-check`
2. Answer the prompts
      ```
      $ checkov --add-check
             _               _
         ___| |__   ___  ___| | _______   __
        / __| '_ \ / _ \/ __| |/ / _ \ \ / /
       | (__| | | |  __/ (__|   < (_) \ V /
        \___|_| |_|\___|\___|_|\_\___/ \_/

      By Prisma Cloud | version: ...

      What action would you like to take? (add) [add]: add

      Enter the title of your new check (without a .py) [MyNewTest]: CheckovIsAwesomeTag

      Select a category for this check (application_security, backup_and_recoveryconvention, encryption, general_security, iam, kubernetes, logging, networking, secrets) [iam]: general_security

      Describe what this check does [Ensure that X does Y...]: Makes sure that aws_iam_policy resources have a tag that says {'Checkov' = IsAwesome'}

      What kind of check would you like to add? (terraform) [terraform]: terraform

      Select the cloud provider this will run on (azure, aws, gcp) [aws]: aws

      Select a terraform object for this check (data, provider, resource) [resource]: resource

      Enter the terraform object type [aws_iam_policy]: aws_iam_policy

      Please ensure you are at the root of the Checkov repository before completing this prompt
      Creating Check CheckovIsAwesomeTag.py in /path/to/checkov/checkov/terraform/checks/resource/aws
          Successfully created /path/to/checkov/checkov/terraform/checks/resource/aws/CheckovIsAwesomeTag.py
      Creating Unit Test Stubs for CheckovIsAwesomeTag in /path/to/checkov/tests/terraform/checks/resource/aws
          Successfully created /path/to/checkov/tests/terraform/checks/resource/aws/example_CheckovIsAwesomeTag/CheckovIsAwesomeTag.tf
          Successfully created /path/to/checkov/tests/terraform/checks/resource/aws/test_CheckovIsAwesomeTag.py

      Next steps:
          1) Edit your new check located in the checks/ directory listed above
          2) Add both a PASS and FAIL unit test to the newly created unit test under the tests/ directory to show others how to fix failures
      ```
3. Go to your new Check at `/path/to/checkov/checkov/terraform/checks/resource/aws/CheckovIsAwesomeTag.py`
4. Edit the `scan_resource_conf()` function to look like the following:
    ```
    def scan_resource_conf(self, conf):
        if 'tags' in conf.keys():
            tags = conf['tags'][0]
            if "Checkov" in tags:
                if tags["Checkov"] == "IsAwesome":
                    return CheckResult.PASSED

        return CheckResult.FAILED
    ```
 
5. Go to your new Unit Test Terraform at `/path/to/checkov/tests/terraform/checks/resource/aws/example_CheckovIsAwesomeTag/CheckovIsAwesomeTag.tf`
6. Edit the terraform resources to contain the following:
    ```
    ## SHOULD PASS: Contains {Checkov: IsAwesome} key/value
    resource "aws_iam_policy" "ckv_unittest_pass" {
      tags = {
        "Checkov" = "IsAwesome"
      }
    }

    ## SHOULD FAIL: Value does not equal "IsAwesome"
    resource "aws_iam_policy" "ckv_unittest_fail" {
      tags = {
        "Checkov" = "IsLame"
      }
    }

    ```
7. Run your tests `pytest -k test_CheckovIsAwesomeTag`
    ```
    $ pytest -k test_CheckovIsAwesome
    ================================================================================ test session starts ================================================================================
    platform darwin -- Python 3.10.14, pytest-6.2.5, py-1.10.0, pluggy-1.0.0
    rootdir: /path/to/checkov
    plugins: xdist-2.4.0, forked-1.3.0, cov-3.0.0
    collected 1952 items / 1951 deselected / 1 selected

    tests/terraform/checks/resource/aws/test_CheckovIsAwesomeTag.py .                                                                                                             [100%]

    ======================================================================== 1 passed, 1951 deselected in 7.16s =========================================================================
    ```
9. Let's add another unit test for a missing tag:
    ```
    ## SHOULD PASS: Contains {Checkov: IsAwesome} key/value
    resource "aws_iam_policy" "ckv_unittest_pass" {
      tags = {
        "Checkov" = "IsAwesome"
      }
    }

    ## SHOULD FAIL: Value does not equal "IsAwesome"
    resource "aws_iam_policy" "ckv_unittest_fail" {
      tags = {
        "Checkov" = "IsLame"
      }
    }

    ## SHOULD FAIL: Missing "Checkov" tag
    resource "aws_iam_policy" "ckv_unittest_fail_1" {
      tags = {
        "SomethingElse" = "IsAwesome"
      }
    }
    ```
10. Run your tests again `pytest -k test_CheckovIsAwesomeTag`
    ```
            ...
            self.assertEqual(summary['passed'], len(passing_resources))
    >       self.assertEqual(summary['failed'], len(failing_resources))
    E       AssertionError: 2 != 1

    tests/terraform/checks/resource/aws/test_CheckovIsAwesomeTag.py:33: AssertionError
    ============================================================================== short test summary info ==============================================================================
    FAILED tests/terraform/checks/resource/aws/test_CheckovIsAwesomeTag.py::TestCheckovIsAwesomeTag::test - AssertionError: 2 != 1
    ======================================================================== 1 failed, 1951 deselected in 7.40s =========================================================================
    ```
11. We failed! Let's fix it. Go to our new Unit Test file `/path/to/checkov/tests/terraform/checks/resource/aws/test_CheckovIsAwesomeTag.py`
12. Notice lines 23-25. Right now, we are configured to only have one failing resource `'aws_iam_policy.ckv_unittest_fail'`
13. Edit `failing_resources` to include our newly added Terraform resource:
    ```
    ...
    passing_resources = {
        'aws_iam_policy.ckv_unittest_pass'
    }
    failing_resources = {
        'aws_iam_policy.ckv_unittest_fail',
        'aws_iam_policy.ckv_unittest_fail_1' # <-- Add this line!
    }
    ...
    ```
14. Run your tests again `pytest -k test_CheckovIsAwesomeTag`
    ```
    $ pytest -k test_CheckovIsAwesome
    ================================================================================ test session starts ================================================================================
    platform darwin -- Python 3.10.14, pytest-6.2.5, py-1.10.0, pluggy-1.0.0
    rootdir: /Users/joseph.meredith/dev/jmeredith18/checkov
    plugins: xdist-2.4.0, forked-1.3.0, cov-3.0.0
    collected 1952 items / 1951 deselected / 1 selected

    tests/terraform/checks/resource/aws/test_CheckovIsAwesomeTag.py .                                                                                                             [100%]

    ======================================================================== 1 passed, 1951 deselected in 6.90s =========================================================================
    ```
15. Go make your own Checks, test them, and contribute! 
   
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
