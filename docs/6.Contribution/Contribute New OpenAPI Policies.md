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

```python
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

And also add the JSON schema to validate the GitHub API response `/checkov/github/schemas/branch_protection.py`:

```python
from checkov.github.schemas.base_schema import GithubConfSchema


class BranchProtectionSchema(GithubConfSchema):
    def __init__(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "url": {
                    "type": "string"
                },
                "required_signatures": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string"
                        },
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "url",
                        "enabled"
                    ]
                },
                "enforce_admins": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string"
                        },
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "url",
                        "enabled"
                    ]
                },
                "required_linear_history": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                },
                "allow_force_pushes": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                },
                "allow_deletions": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                },
                "required_conversation_resolution": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                }
            },
            "required": [
                "url",
                "enforce_admins",
                "required_linear_history",
                "allow_force_pushes",
                "allow_deletions",
            ]
        }
        super().__init__(schema=schema)


schema = BranchProtectionSchema()
```

### Adding a Test

follow the examples in `tests/openapi/test_runner.py` and add a test to the new check

So there you have it! A new check will be scanned once your contribution is merged!
