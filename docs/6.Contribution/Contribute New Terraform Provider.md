---
layout: default
published: true
title: Contribute New Terraform Provider
nav_order: 4
---

# Contribute New Terraform Provider

In this example we'll add support for a new Terraform Provider, the Linode Cloud platform.

## Add Resource Checks for a New Provider

This check is going to examine resources of the type: `linode_instance`, to ensure they have the property `authorised_keys` set.

### Add a Test

First create a new folder `tests/terraform/checks/resource/linode/` and add `test_authorised_keys.py` using the code below:

```python
import unittest

import hcl2

from checkov.terraform.checks.resource.linode.authorized_keys import check
from checkov.common.models.enums import CheckResult


class TestAuthorizedKeys(unittest.TestCase):
    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "linode_instance" "test" {
                authorized_keys="1234355-12345-12-1213123"
            }
            """
        )
        resource_conf = hcl_res["resource"][0]["linode_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "linode_instance" "test" {
            }
            """
        )
        resource_conf = hcl_res["resource"][0]["linode_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == "__main__":
    unittest.main()
```

Add a placeholder file at `tests/terraform/checks/resource/linode/__init__.py`

### Add a Check

Create the folder `checkov/checkov/terraform/checks/resource/linode` and add `authorized_keys.py`:

```python
from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

class AuthorizedKeys(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure SSH key set in authorized_keys"
        id = "CKV_LIN_2"
        supported_resources = ("linode_instance",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "authorized_keys"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AuthorizedKeys() 
```

And also add `checkov/terraform/checks/resource/linode/__init__.py`:

```python
from pathlib import Path

modules = Path(__file__).parent.glob("*.py")
__all__ = [f.stem for f in modules if f.is_file() and not f.stem == "__init__"]
```

### Include Checks

In `checkov/terraform/checks/resource/__init__.py`, update include Linode resources with the entry `from checkov.terraform.checks.resource.linode import *`.
This will ensure that this and any future Linode resource test are included in Checkov runs:

```python
from checkov.terraform.checks.resource.gcp import *  # noqa
from checkov.terraform.checks.resource.azure import *  # noqa
from checkov.terraform.checks.resource.github import *  # noqa
from checkov.terraform.checks.resource.linode import *   # noqa
```

## Add New Provider Checks

This Provider check verifies that the user hasn't added their Linode secret token to their file. Adding the secret token to a Public repository would cause many problems.

### Adding a Test

Create the folder `tests/terraform/checks/provider/linode/` and `test_credentials.py`

```python
import unittest

import hcl2

from checkov.terraform.checks.provider.linode.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):
    def test_success(self):
        hcl_res = hcl2.loads(
            """
            provider "linode" {}
            """
        )
        provider_conf = hcl_res["provider"][0]["linode"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            provider "linode" {
                token = "c7680462065ee80d0fef2940784b1af6826f6e0b18586194c5f67c4b40fa7f09"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["linode"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
```

Then add the placeholder `tests/terraform/checks/provider/linode/__init__.py`

### Add the Provider Check

Create a directory `checkov/terraform/checks/provider/linode` and add `credentials.py`

```python
import re
from typing import Dict, List, Any, Pattern

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck
from checkov.common.models.consts import linode_token_pattern


class LinodeCredentials(BaseProviderCheck):
    def __init__(self):
        name = "Ensure no hard coded Linode tokens exist in provider"
        id = "CKV_LIN_1"
        supported_provider = ("linode",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if self.secret_found(conf, "token", linode_token_pattern):
            return CheckResult.FAILED
        return CheckResult.PASSED

    @staticmethod
    def secret_found(conf: Dict[str, List[Any]], field: str, pattern: Pattern[str]) -> bool:
        if field in conf.keys():
            value = conf[field][0]
            if re.match(pattern, value) is not None:
                return True
        return False


check = LinodeCredentials()
```

And also `checkov/terraform/checks/provider/linode/__init__.py`

```python
from pathlib import Path

modules = Path(__file__).parent.glob("*.py")
__all__ = [f.stem for f in modules if f.is_file() and not f.stem == "__init__"]
```

Update the security constants `checkov/common/models/consts.py` with the new pattern.

```python
import re
SUPPORTED_FILE_EXTENSIONS = [".tf", ".yml", ".yaml", ".json", ".template"]
ANY_VALUE = "CKV_ANY"
DOCKER_IMAGE_REGEX = re.compile(r'(?:[^\s\/]+/)?([^\s:]+):?([^\s]*)')
access_key_pattern = re.compile(r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])") # nosec
secret_key_pattern = re.compile("(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])") # nosec
linode_token_pattern = re.compile("(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{64}(?![A-Za-z0-9/+=])") # nosec
```

### Include the Provider Checks

Update `checkov/terraform/checks/provider/__init__.py` with `from checkov.terraform.checks.provider.linode import *`, making it:

```python
from checkov.terraform.checks.provider.aws import *  # noqa
from checkov.terraform.checks.provider.linode import *  # noqa
```

So there you have it! Two new checks—one for your resource and a newly supported Terraform Provider.
