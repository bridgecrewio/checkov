---
layout: default
published: true
title: Contribute New Bitbucket configuration policy
nav_order: 5
---

# Contribute New Bitbucket configuration policy

In this example, we'll add support for a new Bitbucket configuration check.

## Add new API call to fetch data from Bitbucket

We are going to add a new check that will examine how branch protection rules are configured and validate we enforce protection rules on admin users too.

### Add an API call

First, we will validate if the Bitbucket API call that GETs the branch protection current state exists in `checkov/bitbucket/dal.py`.
If not it can be added to that file like the following example:

```python

class Bitbucket(BaseVCSDAL)
    ...
    ...

    def get_branch_restrictions(self):
        if self.current_repository:
            branch_restrictions = self._request(
                endpoint=f"repositories/{self.current_repository}/branch-restrictions")
            return branch_restrictions
        return None

    def persist_branch_restrictions(self):
        branch_restrictions = self.get_branch_restrictions()

        if branch_restrictions:
            BaseVCSDAL.persist(path=self.bitbucket_branch_restrictions_file_path, conf=branch_restrictions)

    def persist_all_confs(self):
        if strtobool(os.getenv("CKV_BITBUCKET_CONFIG_FETCH_DATA", "True")):
            self.persist_branch_restrictions()

```

### Add a Check

Go to `checkov/bitbucket/checks` and add `enforce_branch_protection_on_admins.py`:

```python
from checkov.bitbucket.base_bitbucket_configuration_check import BaseBitbucketCheck
from checkov.bitbucket.schemas.branch_restrictions import schema as branch_restrictions_schema
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json_doc.enums import BlockType


class MergeRequestRequiresApproval(BaseBitbucketCheck):
    def __init__(self):
        name = "Merge requests should require at least 2 approvals"
        id = "CKV_BITBUCKET_1"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf):
        if branch_restrictions_schema.validate(conf):
            for value in conf.get("values", []):
                if value.get('kind', '') == 'require_approvals_to_merge':
                    if value.get('value', 0) >= 2:
                        return CheckResult.PASSED, conf
            return CheckResult.FAILED, conf


check = MergeRequestRequiresApproval()

```

And also add the JSON schema to validate the Bitbucket API response `/checkov/bitbucket/schemas/branch_protection.py`:

```python
from checkov.common.vcs.vcs_schema import VCSSchema


class BranchRestrictionsSchema(VCSSchema):
    def __init__(self):
        schema = \
            {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "object",
                "properties": {
                    "pagelen": {
                        "type": "integer"
                    },
                    "values": {
                        "type": "array",
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "kind": {
                                        "type": "string"
                                    },
                                    "users": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "links": {
                                        "type": "object",
                                        "properties": {
                                            "self": {
                                                "type": "object",
                                                "properties": {
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                },
                                                "required": [
                                                    "href"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "self"
                                        ]
                                    },
                                    "pattern": {
                                        "type": "string"
                                    },

                                    "branch_match_kind": {
                                        "type": "string"
                                    },
                                    "groups": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "kind",
                                    "users",
                                    "links",
                                    "pattern",
                                    "branch_match_kind",
                                    "groups",
                                    "type",
                                    "id"
                                ]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "kind": {
                                        "type": "string"
                                    },
                                    "users": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "links": {
                                        "type": "object",
                                        "properties": {
                                            "self": {
                                                "type": "object",
                                                "properties": {
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                },
                                                "required": [
                                                    "href"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "self"
                                        ]
                                    },
                                    "pattern": {
                                        "type": "string"
                                    },

                                    "branch_match_kind": {
                                        "type": "string"
                                    },
                                    "groups": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "kind",
                                    "users",
                                    "links",
                                    "pattern",
                                    "branch_match_kind",
                                    "groups",
                                    "type",
                                    "id"
                                ]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "kind": {
                                        "type": "string"
                                    },
                                    "users": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "links": {
                                        "type": "object",
                                        "properties": {
                                            "self": {
                                                "type": "object",
                                                "properties": {
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                },
                                                "required": [
                                                    "href"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "self"
                                        ]
                                    },
                                    "pattern": {
                                        "type": "string"
                                    },

                                    "branch_match_kind": {
                                        "type": "string"
                                    },
                                    "groups": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "kind",
                                    "users",
                                    "links",
                                    "pattern",
                                    "branch_match_kind",
                                    "groups",
                                    "type",
                                    "id"
                                ]
                            }
                        ]
                    },
                    "page": {
                        "type": "integer"
                    },
                    "size": {
                        "type": "integer"
                    }
                },
                "required": [
                    "pagelen",
                    "values",
                    "page",
                    "size"
                ]
            }
        super().__init__(schema=schema)


schema = BranchRestrictionsSchema()

```

### Adding a Test

follow the examples in `tests/bitbucket/test_runner.py` and add a test to the new check

So there you have it! A new check will be scanned once your contribution is merged!
