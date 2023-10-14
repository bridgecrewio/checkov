---
layout: default
published: true
title: Migration
nav_order: 5
---

# Migration - v2 to v3

With v3 not only new features were added, but following behaviour changed or was completely removed.
We plan to release the new version end of October 2023.

## Remove of "level up"

Since Bridgecrew standalone edition will be shutting down at the [end of 2023](https://www.paloaltonetworks.com/services/support/end-of-life-announcements) we removed the "level up" flow, 
which is triggered by just running `checkov` without any flag.

## Python custom checks

If you are still using the old syntax of running your custom code

```python
from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class Example(BaseResourceCheck):
    ...

    def scan_resource_conf(self, conf: dict[str, list[Any]], entity_type: str) -> CheckResult:
        ...
```

then you can easily use the simplified syntax and still access `entity_type`, if needed

```python
from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class Example(BaseResourceCheck):
    ...

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if self.entity_type == 'aws_instance':
            ...
        
        ...
```
