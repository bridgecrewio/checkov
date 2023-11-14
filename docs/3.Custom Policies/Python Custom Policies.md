---
layout: default
published: true
title: Python Custom Policies
nav_order: 2
---

# Create Custom Policy - Python - Attribute Check

Custom Policies created in code (in Python) support checking the state of a resource’s attributes.
A Python-based Custom Policy for Checkov consists of sections for Metadata and Policy Definition.

Read also how to [create custom YAML Policies for attribute and composite scanning](https://www.checkov.io/3.Custom%20Policies/YAML%20Custom%20Policies.html).

## Writing a Python custom Checkov policy

Specify a `name`, `ID`, `relevant resources` and `categories`.

| Parameter                         | Description                                                                                                                                                                                                                    | Example/Comments                                                                                                                                                                               |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ``name``                          | A new policy's unique purpose. It should ideally specify the positive desired outcome of the policy.                                                                                                                           |                                                                                                                                                                                                |
| ``id``                            | A mandatory unique identifier of a policy. Native policies written by Prisma Cloud contributors will follow the following convention: ``CKV_providerType_serialNumber``                                                          | `CKV_AWS_9` , `CKV_GCP_12`                                                                                                                                                                                                     |
| ``supported_resources``           | Infrastructure objects, as described in the scanned IaC's language. This usually contains one specific resource block. If you support multiple resources, you can use `*` to match any type of entity in that specific domain. | `*` use depends on which check base class you extend; see note below table. `?ws_*` will match anything where the second character is a `'w'`, the third is a `'s'` and the fourth is a `'_'`. |
| ``categories``                    | Categorization of a scan. Usually used to produce compliance reports, pipeline analytics and infrastructure health metrics, etc.                                                                                               |                                                                                                                                                                                                |
| ``guideline``                     | (Optional) Add extra info to help the user to solve the issue.                                                                                                                                                                 | This is not needed                                                                                                                                                                             |

**Note for Supported Resources Parameter:** If you extend `checkov.terraform.checks.resource.base_resource_check.BaseResourceCheck`, the check is registered for all Terraform resources.

The following example produces a policy that ensures that new RDS services spun-up are encrypted at rest, given a scanned Terraform configuration ([CKV_AWS_16](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/aws/RDSEncryption.py)).
1. Create a new file in the AWS check directory ``checkov/terraform/checks/resource/aws/RDSEncryption.py``.
2. Import the following:

```python
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
```

3. Define the meta entities for this check as described in the table above.

```python
class RDSEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_16"
        supported_resources = ("aws_db_instance",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
```

4. Define a simple check of the ```aws_db_instance``` resource block to determine if ```aws_db_instance``` is disabled. If it is disabled, that needs to cause a ```CheckResult.FAILED``` to occur.

```python
def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
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

**Note:**

The `conf` parameter is dependent on the resource type, which was chosen via the `supported_resources` class instance attribute.
For example, for the `aws_db_instance` resource, we get the following value:

```python
conf = {
    "__end_line__": 11,  # internal field
    "__start_line__": 3,  # internal field
    "allocated_storage": [5],
    "enabled_cloudwatch_logs_exports": [["postgresql", "upgrade"]],
    "engine": ["postgres"],
    "instance_class": ["db.t3.small"],
    "password": ["postgres"],
    "username": ["postgres"],
    "__address__": "aws_db_instance.postgres",  # internal field
}
```

which is the internal representation of following Terraform resource block

```hcl
resource "aws_db_instance" "postgres" {
  allocated_storage = 5
  engine            = "postgres"
  instance_class    = "db.t3.small"
  password          = "postgres"
  username          = "postgres"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}
```

If more than one resource type was set for `supported_resources`, then it is possible to retrieve the info via the class instance attribute `self.entity_type`.

```python
def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
    if self.entity_type == "aws_db_instance":
        ...
    elif self.entity_type == "aws_rds_cluster_instance":
        ...
```

5. Implement `get_evaluated_keys` to allow the check results report show the specified key.

```python
def get_evaluated_keys(self) -> List[str]:
    return ['storage_encrypted/[0]']
```

If the evaluated keys are determined dynamically, you can set the evaluated key when scanning the resource configuration:
```python
def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
    """
        Looks for encryption configuration at aws_db_instance:
        https://www.terraform.io/docs/providers/aws/d/db_instance.html
    :param conf: aws_db_instance configuration
    :return: <CheckResult>
    """
    if 'storage_encrypted' in conf.keys():
        key = conf['storage_encrypted'][0]
        if key:
            # The following line sets the evaluated keys
            self.evaluated_keys = ['storage_encrypted/[0]']
            return CheckResult.PASSED
    return CheckResult.FAILED
```

6. You can also add `details` to be printed on the execution report:
```python
def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
    """
        Looks for encryption configuration at aws_db_instance:
        https://www.terraform.io/docs/providers/aws/d/db_instance.html
    :param conf: aws_db_instance configuration
    :return: <CheckResult>
    """
    if 'storage_encrypted' in conf.keys():
        key = conf['storage_encrypted'][0]
        if key:
            # The following line sets the evaluated keys
            self.evaluated_keys = ['storage_encrypted/[0]']
            return CheckResult.PASSED
        
    self.details.append("'storage_encrypted' was not found on the resource configuration")
    
    return CheckResult.FAILED
```

Produces the following CLI report:
![details-cli-screenshot](https://raw.githubusercontent.com/bridgecrewio/checkov/main/docs/checkov-scan-cli-details.png)

7. Conclude the policy name and operationalize it with the statement:

```python
check = RDSEncryption()
```

### Selecting the best base check class to extend
Terraform and CloudFormation have two base classes extending `BaseResourceCheck`:

1. **BaseResourceValueCheck**: This check will pass only if the `inspected_key` is within the `expected_values`. If `get_expected_value` is not implemented, the default value is `[True]`. 

```python
class RDSPubliclyAccessible(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in RDS is not publicly accessible"
        id = "CKV_AWS_17"
        supported_resources = ("AWS::RDS::DBInstance",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)
    
    def get_inspected_key(self) -> str:
        return 'Properties/PubliclyAccessible'    
        
    def get_expected_values(self) -> list[Any]:
        return [False]
```

Another option is to use `ANY_VALUE`:
```python
def get_expected_values(self) -> list[Any]:
    return [ANY_VALUE]
```

2. **BaseResourceNegativeValueCheck**: This check will pass only if the `inspected_key` is NOT within the `forbidden_values`. 

```python
class NeptuneClusterInstancePublic(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Neptune Cluster instance is not publicly available"
        id = "CKV_AWS_102"
        supported_resources = ['aws_neptune_cluster_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'publicly_accessible/[0]'

    def get_forbidden_values(self) -> List[Any]:
        return [True]
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
from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class S3PCIPrivateACL(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure PCI Scope buckets has private ACL (enable public ACL for non-pci buckets)"
        id = "CKV_AWS_999"
        supported_resources = ("aws_s3_bucket",)
        # CheckCategories are defined in models/enums.py
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        guideline = "Follow the link to get more info https://docs.prismacloud.io/en/enterprise-edition/policy-reference"
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        """
            Looks for ACL configuration at aws_s3_bucket and Tag values:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        tags = conf.get("tags")
        if tags and isinstance(tags, list):
            tags = tags[0]
            if tags.get("Scope") == "PCI":
                acl_block = conf['acl']
                if acl_block in [["public-read"], ["public-read-write"], ["website"]]:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = S3PCIPrivateACL()
```

2. With the new custom check in place, run Checkov:

```python
# install from pypi using pip
pip install checkov


# select an input folder that contains your terraform files and enable loading of extra checks
checkov -d . --external-checks-dir my_extra_checks
```
Verify the results:

```shell
Check: "Ensure PCI Scope buckets has private ACL (enable public ACL for non-pci buckets)"
	FAILED for resource: aws_s3_bucket.credit_cards_bucket
	File: /main.tf:80-90
	Guide: Follow the link to get more info https://docs.prismacloud.io/en/enterprise-edition/policy-reference

		80 | resource "aws_s3_bucket" "credit_cards_bucket" {
		81 |   region        = var.region
		82 |   bucket        = local.bucket_name
		83 |   acl           = "public-read"
		84 |   force_destroy = true
		85 |
		86 |   tags = {
		87 |     Scope = "PCI",
		88 |
		89 |   }
		90 | }
```

**Attention:** Policies cannot share the same file name. If two policies with the same file name exist, only the first one will be loaded.
