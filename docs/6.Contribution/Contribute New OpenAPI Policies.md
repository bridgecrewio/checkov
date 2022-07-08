                                                                                     ---
layout: default
published: true
title: Contribute New OpenAPI configuration policy
nav_order: 5
---

# Contribute New OpenAPI configuration policy

In this example, we'll add support for a new OpenAPI configuration check.


### Add a Check

Go to `checkov/openapi/checks/resource`, go to v2|v3|generic according to the OpenAPI version you check and add `GlobalSecurityFieldIsEmpty.py`:

v2 - OpenAPI 2.0.  
v3 - OpenAPI 3.  
generic - for both OpenAPI 2 and 3.

In case the check is for OpenAPI version 2.0, use parent class `BaseOpenapiCheckV2` and override check method `scan_openapi_conf`
In case the check is for OpenAPI version 3, use parent class `BaseOpenapiCheckV3` and override check method `scan_openapi_conf`
In case the check is a generic check for OpenAPI version 2.0 and 3, use parent class `BaseOpenapiCheck` and override check method `scan_entity_conf`

```python
from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck

class GlobalSecurityFieldIsEmpty(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_4"
        name = "Ensure that the global security field has rules defined"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['security']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        security_rules = conf.get("security")

        if security_rules:
            return CheckResult.PASSED, security_rules
        return CheckResult.FAILED, conf


check = GlobalSecurityFieldIsEmpty()
```

### Adding a Test

follow the examples in `tests/openapi/test_runner.py` and add a test to the new check

So there you have it! A new check will be scanned once your contribution is merged!
