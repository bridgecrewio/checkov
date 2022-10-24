---
layout: default
published: true
title: Contribute New Gitlab configuration policy
nav_order: 5
---

# Contribute New Gitlab configuration policy

In this example, we'll add support for a new Gitlab configuration check.

## Add new API call to fetch data from Gitlab

We are going to add a new check that will examine how merge requests protection rules are configured and validate we enforce at least 2 approvers.

### Add an API call

First, we will validate if the Gitlab API call that GETs the branch protection current state exists in `checkov/gitlab/dal.py`.
If not it can be added to that file like the following example:

```python

class Gitlab(BaseVCSDAL):
    ...
    ...
    def get_project_approvals(self):
        if self.project_id:
            project_approvals = self._request(
                endpoint=f"projects/{self.project_id}/approvals")
            return project_approvals
        return None

    def persist_project_approvals(self):
        project_approvals = self.get_project_approvals()

        if project_approvals:
            BaseVCSDAL.persist(path=self.gitlab_project_approvals_file_path, conf=project_approvals)   
    
    def persist_all_confs(self):
        if strtobool(os.getenv("CKV_GITLAB_CONFIG_FETCH_DATA", "True")):
            self.persist_project_approvals()
            self.persist_groups()

```

### Add a Check

Go to `checkov/gitlab/checks` and add `enforce_branch_protection_on_admins.py`:

```python
class MergeRequestRequiresApproval(BaseGitlabCheck):
    def __init__(self):
        name = "Merge requests should require at least 2 approvals"
        id = "CKV_GITLAB_1"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf):
        if project_aprovals_schema.validate(conf):
            if conf.get("approvals_before_merge", 0) < 2:
                return CheckResult.FAILED, conf
            return CheckResult.PASSED, conf


check = MergeRequestRequiresApproval()

```

And also add the JSON schema to validate the Gitlab API response `/checkov/gitlab/schemas/project_approvals.py`:

```python

from checkov.common.vcs.vcs_schema import VCSSchema


class ProjectApprovalsSchema(VCSSchema):
    def __init__(self):
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "approvals_before_merge": {
                    "type": "integer"
                },
                "reset_approvals_on_push": {
                    "type": "boolean"
                },
                "disable_overriding_approvers_per_merge_request": {
                    "type": "boolean"
                },
                "merge_requests_author_approval": {
                    "type": "boolean"
                },
                "merge_requests_disable_committers_approval": {
                    "type": "boolean"
                },
                "require_password_to_approve": {
                    "type": "boolean"
                }
            },
            "required": [
                "approvals_before_merge",
                "reset_approvals_on_push",
                "disable_overriding_approvers_per_merge_request",
                "merge_requests_author_approval",
                "merge_requests_disable_committers_approval",
                "require_password_to_approve"
            ]
        }
        super().__init__(schema=schema)


schema = ProjectApprovalsSchema()

```

### Adding a Test

follow the examples in `tests/gitlab/test_runner.py` and add a test to the new check

So there you have it! A new check will be scanned once your contribution is merged!
