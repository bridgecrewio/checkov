---
layout: default
published: true
title: Custom Scans
order: 6
---

# Custom Scans

Checkov is delivered with a  [set of built-in policies](../3.Scans/resource-scans.md) that checks for compliance and security best practices at its core.
 In addition, Checkov enables loading of extra checks, that give the user a possibility to author and execute custom policies.

# Example 
Let's assume we have the following directory structure:
```text
├── main.tf
├── variables.tf
└── outputs.tf
```
And that we have a unique need to enforce bucket ACL policies only when the tag `Scope=PCI` is present.  
In other words, as security-aware engineers, we want the following bucket definition will trigger a failed check result:

```hcl-terraform
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
For that we will need to add a new check to ensure PCI related S3 buckets will stay private.
So we will create a new python folder named `my_extra_checks` containing our new check 

```text
├── main.tf
├── variables.tf
└── outputs.tf
└── my_extra_checks
    └── __init__.py
    └── S3PCIPrivateACL.py

```

And we will fill the matching logic in `S3PCIPrivateACL.py`:
```python
from lark import Token

from checkov.terraform.checks.resource.base_check import BaseResourceCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories


class S3PCIPrivateACL(BaseResourceCheck):
    def __init__(self):
        name = "Ensure PCI Scope buckets has private ACL (enable public ACL for non-pci buckets)"
        id = "CKV_AWS_999"
        supported_resources = ['aws_s3_bucket']
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
Now that we have the new custom check in place, we can run Checkov and verify the results:

```bash
# install from pypi using pip
pip install checkov


# select an input folder that contains your terraform files and enable loading of extra checks
checkov -d . --extra-checks my_extra_checks
```

Results:

```bash
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