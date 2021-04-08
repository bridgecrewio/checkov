---
layout: default
published: true
title: Python Custom Policies
nav_order: 2
---

# Create Custom Policy - Python - Attribute Check

Custom Policies created in code (in Python) support checking the state of a resource’s attributes.
A Python-based Custom Policy for Checkov consists of sections for Metadata and Policy Definition.

Read also how to [create custom YAML Policies for attribute and composite scanning](../3.Custom%20Policies/YAML%20Custom%20Policies.md).

## Writing a Python custom Checkov policy

Specify a `name`, `ID`, `relevant resources` and `categories`.

| Parameter | Description | Example/Comments |
| -------- | -------- | -------- |
| ``name`` | A new policy's unique purpose. It should ideally specify the positive desired outcome of the policy. |  |
| ``id`` | A mandatory unique identifier of a policy. Native policies written by Bridgecrew contributors will follow the following convention:
``CKV_providerType_serialNumber`` | `CKV_AWS_9` , `CKV_GCP_12` |
| ``supported_resources`` | Infrastructure objects, as described in the scanned IaC's language. This usually contains one specific resource block. If you support multiple resources, you can use `*` to match any type of entity in that specific domain. | `*` use depends on which check base class you extend; see note below table. `?ws_*` will match anything where the second character is a `'w'`, the third is a `'s'` and the fourth is a `'_'`. |
| ``categories`` | Categorization of a scan. Usually used to produce compliance reports, pipeline analytics and infrastructure health metrics, etc. |  |

**Note for Supported Resources Parameter:** If you extend `checkov.terraform.checks.resource.base_resource_check.BaseResourceCheck`, the check is registered for all Terraform resources.

The following example produces a policy that ensures that new RDS services spun-up are encrypted at rest, given a scanned Terraform configuration ([CKV_AWS_16](https://github.com/bridgecrewio/checkov/blob/master/checkov/terraform/checks/resource/aws/RDSEncryption.py)).
1. Create a new file in the AWS check directory ``checkov/terraform/checks/resource/aws/RDSEncryption.py``.
2. Import the following:

```python
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
```

3. Define the meta entities for this check as described in the table above.

```python
class RDSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_16"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
```

4. Define a simple check of the ```aws_db_instance``` resource block to determine if ```aws_db_instance``` is disabled. If it is disabled, that needs to cause a ```CheckResult.FAILED``` to occur.

```python
def scan_resource_conf(self, conf):
    """
        Looks for encryption configuration at aws_db_instance:
        https://www.terraform.io/docs/providers/aws/d/db_instance.html
    :param conf: aws_db_instance configuration
    :return: <CheckResult>
    """
    if 'storage_encrypted' in conf.keys():
        key = conf['storage_encrypted'][0]
        if key:
            return CheckResult.PASSED
    return CheckResult.FAILED
```

5. Conclude the policy name and operationalize it with the statement:

```python
check = RDSEncryption()
```

### Run a new scan

To run a scan with the new policy, use the ```checkov``` command.

```python
checkov -d /user/tf
```


#Working with Custom Policies

Checkov is delivered with a set of built-in policies that check for compliance and security best practices at its core. In addition, Checkov enables you to load additional checks, that give the user the ability to author and execute custom policies.

## Example 
This example uses the following directory structure:

```text
├── main.tf
├── variables.tf
└── outputs.tf
```

The example assumes a unique need to enforce bucket ACL policies only when the tag `Scope=PCI` is present.  That being the case, the following bucket definition must trigger a failed check result:

```python
# Snippet from  main.tf
resource "aws_s3_bucket" "credit_cards_bucket" {
  region        = var.region
  bucket        = local.bucket_name
  acl           = "public-read"
  force_destroy = true

  tags = {
    Scope = "PCI",
    
  }
}
```

To trigger the failed check result, you need to add a new check to ensure PCI related S3 buckets will stay private.
1. Create a new python folder named `my_extra_checks` containing the new check:

```text
├── main.tf
├── variables.tf
└── outputs.tf
└── my_extra_checks
    └── __init__.py
    └── S3PCIPrivateACL.py
```

  a. The first time you setup the custom checks folder, you need to also create a file named `__init__.py`.

```python
from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
```

  b. Complete the matching logic in `S3PCIPrivateACL.py`:

```python
from lark import Token

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class S3PCIPrivateACL(BaseResourceCheck):
    def __init__(self):
        name = "Ensure PCI Scope buckets has private ACL (enable public ACL for non-pci buckets)"
        id = "CKV_AWS_999"
        supported_resources = ['aws_s3_bucket']
        # CheckCategories are defined in models/enums.py
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for ACL configuration at aws_s3_bucket and Tag values:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'tags' in conf.keys():
            environment_tag = Token("IDENTIFIER", "Scope")
            if environment_tag in conf['tags'][0].keys():
                if conf['tags'][0][environment_tag] == "PCI":
                    if 'acl' in conf.keys():
                        acl_block = conf['acl']
                        if acl_block in [["public-read"], ["public-read-write"], ["website"]]:
                            return CheckResult.FAILED
        return CheckResult.PASSED


scanner = S3PCIPrivateACL()
```

2. With the new custom check in place, run Checkov:

```python
# install from pypi using pip
pip install checkov


# select an input folder that contains your terraform files and enable loading of extra checks
checkov -d . --external-checks-dir my_extra_checks
```
Verify the results:

```python
Check: "Ensure PCI Scope buckets has private ACL (enable public ACL for non-pci buckets)"
	FAILED for resource: aws_s3_bucket.credit_cards_bucket
	File: /main.tf:80-90

		80 | resource "aws_s3_bucket" "credit_cards_bucket" {
		81 | region        = var.region
		82 | bucket        = local.bucket_name
		83 | acl           = "public-read"
		84 | force_destroy = true
		85 | 
		86 | tags = {
		87 | Scope = "PCI",
		88 | 
		89 | }
		90 | }
```

**Attention:** Policies cannot share the same file name. If two policies with the same file name exist, only the first one will be loaded.
