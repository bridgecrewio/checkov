---
layout: default
published: true
title: Create Policies for New Provider
order: 4
---
This check is going to examine resources of the type: `linode_instance`, to ensure they have the property `authorised_keys` set.

### Add a Test for Custom Policy
Create a new folder `tests/terraform/checks/resource/linode/` and add the file `test_authorised_keys.py` using the following code:

```python
import unittest

import hcl2
from checkov.terraform.checks.resource.linode.authorized_keys import check
from checkov.common.models.enums import CheckResult


class Testauthorized_keys(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "linode_instance" "test" {
        authorized_keys="1234355-12345-12-1213123"
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "linode_instance" "test" {
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
```

Add a placeholder file at `tests/terraform/checks/resource/linode/__init__.py`
```python

```

### Add the Custom Policy
Create the folder `checkov/checkov/terraform/checks/resource/linode` and add the file `authorized_keys.py` using the following code:

```python
```

Add `checkov/terraform/checks/resource/linode/__init__.py` using the following code:

```python
```

### Include the Custom Policy
In `checkov/terraform/checks/resource/__init__.py`, update include Linode resources with the entry `from checkov.terraform.checks.resource.linode import *`.
This will ensure that this and any future Linode resource test are included in Checkov runs:

```python
```

## Add Custom Policies for New Provider
This Provider check verifies that the user hasn't added their Linode secret token to their file. Adding the secret token to a Public repository, would cause many problems.

### Adding a Test
Create the folder `tests/terraform/checks/provider/linode/` and the file `test_credentials.py`.

```python
```

Add the placeholder `tests/terraform/checks/provider/linode/__init__.py`:
```python

```

### Add the Provider check
Create a directory `checkov/terraform/checks/provider/linode` and add the file `credentials.py`.

```python
```

Add the file `checkov/terraform/checks/provider/linode/__init__.py`.
Update the security constants `checkov/common/models/consts.py` with the new pattern:

```python
```

```python
```

### Include the Provider checks
Update `checkov/terraform/checks/provider/__init__.py` with `from checkov.terraform.checks.provider.linode import *` making it:

```python
```

So there you have it! Two new checks—one for your resource and a newly supported Terraform Provider.
