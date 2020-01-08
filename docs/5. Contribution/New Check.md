# Contribute a new check

Checkov contributors are more than welcomed to contribute new checks. With more implemented checks, Checkov's ability to
detect various security and compliance misconfigurations improves. 

This guide covers all the necessary steps required for contributing a new check.

## Prerequisites
### Installation
Make sure you have installed and configured Checkov correctly, by reading the [Getting Started](../1.Introduction/Getting%20Started.md)
page.
It is encouraged to run Checkov in order to get familiar with it's functionality.

### What is a check?
Checkov's goal is to scan cloud infrastructure provisioned using Terraform and detect security and compliance misconfigurations.
This is achieved by applying Checkov's checks on the scanned Terraform configuration.

A check consists of at least the following mandatory properties:

``name`` : A new check's unique purpose; It should ideally specify the positive desired outcome of the policy.

``id``: A mandatory unique identifier of a policy; Native policies written by Bridgecrew contributors will follow the following convention ``CKV_providerType_serialNumber``. (e.g. `CKV_AWS_9` , `CKV_GCP_12`)

``categories``: Categorization of a scan; usually used to produce compliance reports, pipeline analytics and infrastructure health metrics, etc.

Note: When contributing a new check, please increment the `id`'s serial number to be `x+1`, where `x` is the serial number
of the latest implemented check, with respect to the check's provider.

A more specific type of check may also include additional attributes. For example, a check that scans a Terraform resource
configuration also contains the `supported_resources` attribute, which is a list of the supported resource types of the check.

### Check result

The check's result on a scanned configuration tells if the configuration complied by the check's policy, which means, 
a binary result of either `PASSED` or `FAILED`. an `UNKNOWN` option is also included, which means that it is unknown if 
the scanned configuration complied with the check.

Furthermore, a check can be suppressed by Checkov on a given configuration by inserting a skip comment inside a specific
configuration scope. Then, the check's result on the suppressed configuration would be `SKIPPED`.      
Read more about Checkov's [Suppressions](../3.Scans/resource-scans.md) for further details.
 
### Check type and provider
Checkov's check should relate to a common Terraform configuration type of certain provider. 
For example, a check that validates the encryption configuration of an S3 bucket is considered to be of type `resource`,
and of `aws` provider. 

Identify the type and provider of the new check in order to place it correctly under the project structure.
For example, the mentioned above check is already implemented in Checkov under `checkov/terraform/checks/resource/aws/S3Encryption.py`.

As seen, checks are divided first to folders grouped by their type, and are after divided by their provider.

### Check's Terraform configuration documentation

If available, please provide the official [Terraform](https://www.terraform.io/docs) documentation of the checked 
configuration. This helps users to better understand the check's scanned configuration and it's usage.

For example, the mentioned above check's configuration documentation can be found [here](https://www.terraform.io/docs/providers/aws/r/s3_bucket.html) 

### Example Terraform configuration
In order to develop the check, a relevant example configuration should be presented as an input to Checkov.
Provide an example configuration (`example.tf`) that contains both passing and failing configurations with respect to 
the check's logic.
The file can be served as an input to the appropriate check's unit tests. 

## Implementation

After identifying the check's type and provider, place the file containing it's code inside `checkov/terraform/checks/<type>/<provider>`,
where `<type>` is the check's type and `<provider>` is the check's provider.
A check is a class implementing an `abstract` base check class that corresponds to some provider and type. 

For example, all checks of `resource` type and `aws` provider are implementing the resource base check class found at 
`checkov/terraform/checks/resource/base_check.py`. The resource check needs to implement it's base check's abstract method named 
`scan_resource_conf`, which accepts as an input a dictionary of all the key-valued resource attributes, and outputs a `CheckResult`.

For a full implementation example of a check, please refer the [Policies documentation](../1.Introduction/Policies.md).

## Testing

Assuming the implemented check's class is file is found in `checkov/terraform/checks/<type>/<provider>` directory, named
`<ClassName>.py`, create an appropriate unit test file in `tests/terraform/checks/<type>/<provider>` directory, named 
`test_<ClassName>.py`.

The test suite should cover different check results; Test if the check outputs `PASSED` on a compliant configuration,
and test if it output `FAILED` on a non-compliant configuration. You are also encouraged to test more specific 
components of the check, according to their complexity.
