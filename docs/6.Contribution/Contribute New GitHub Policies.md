---
layout: default
published: true
title: Contribute New GitHub configuration policy
nav_order: 5
---

# Contribute New GitHub configuration policy

In this example, we'll add support for a new GitHub configuration check.

## Add new API call to fetch data from GitHub

We are going to add a new check that will examine how branch protection rules are configured and validate we enforce protection rules on admin users too.

### Add an API call

First, we will validate if the GitHub API call that GETs the branch protection current state exists in `checkov/github/dal.py`.
If not it can be added to that file like the following example:

```python

class GitHub(BaseVCSDAL):
    ...
    ...
    def setup_conf_dir(self) -> None:
        ...
        self.github_conf_file_paths = {
            "branch_protection_rules": [Path(self.github_conf_dir_path) / "branch_protection_rules.json"],
            ...
        }
        
    def get_branch_protection_rules(self):
        if self.current_branch and self.current_repository:
            branch_protection_rules = self._request(
                endpoint="repos/{}/branches/{}/protection".format(self.current_repository, self.current_branch))
            return branch_protection_rules
        return None
    
    def persist_branch_protection_rules(self):
        data = self.get_branch_protection_rules()
        if data:
            BaseVCSDAL.persist(path=self.github_conf_file_paths["branch_protection_rules"][0], conf=data)        
    
    def persist_all_confs(self):
        if strtobool(os.getenv("CKV_GITHUB_CONFIG_FETCH_DATA", "True")):
            self.persist_organization_security()
            self.persist_branch_protection_rules()
```

### Add a Check

Go to `checkov/github/checks` and add `enforce_branch_protection_on_admins.py`:

```python
from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchEnforceAdmins(BranchSecurity):
    def __init__(self):
        name = "Ensure GitHub branch protection rules is enforced on admins"
        id = "CKV_GITHUB_8"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self):
        return ['enforce_admins/enabled']


check = GithubBranchEnforceAdmins()
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

follow the examples in `tests/github/test_runner.py` and add a test to the new check

So there you have it! A new check will be scanned once your contribution is merged!
