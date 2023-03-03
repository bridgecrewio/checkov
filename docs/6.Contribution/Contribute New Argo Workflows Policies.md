---
layout: default
published: true
title: Contribute New Argo Workflows configuration policy
nav_order: 5
---

# Contribute New Argo Workflows configuration policy

In this example, we'll add support for a new Argo Workflows configuration check to validate the usage of a user defined ServiceAccount.

## Add a Check

Go to `checkov/argo_workflows/checks/template` and add `DefaultServiceAccount.py`:

```python
from __future__ import annotations

from typing import Any

from checkov.argo_workflows.checks.base_argo_workflows_check import BaseArgoWorkflowsCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class DefaultServiceAccount(BaseArgoWorkflowsCheck):
    def __init__(self) -> None:
        name = "Ensure Workflow pods are not using the default ServiceAccount"
        id = "CKV_ARGO_1"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.IAM,),
            supported_entities=("spec",),
            block_type=BlockType.OBJECT,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if "serviceAccountName" in conf.keys() and conf["serviceAccountName"] != "default":
            return CheckResult.PASSED, conf

        return CheckResult.FAILED, conf


check = DefaultServiceAccount()
```

### Adding a Test

Create a new folder under `tests/argo_workflows/checks/template` with the name of your check `example_DefaultServiceAccount` for adding example configuration files.
Try to add at least 2 test cases, one passing and one failing. 

`pass.yaml`:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  serviceAccountName: custom-sa
  entrypoint: whalesay
  templates:
  - name: whalesay
    container:
      image: docker/whalesay:latest
      command: [cowsay]
      args: ["hello world"]
```

Lastly add the test file `test_DefaultServiceAccount.py` to scan the example files.

```python
from pathlib import Path

from checkov.argo_workflows.runner import Runner
from checkov.argo_workflows.checks.template.DefaultServiceAccount import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_DefaultServiceAccount"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        f"{test_files_dir}/pass.yaml.spec.spec.CKV_ARGO_1[6:14]",
    }

    failing_resources = {
        f"{test_files_dir}/fail_default.yaml.spec.spec.CKV_ARGO_1[6:14]",
        f"{test_files_dir}/fail_none.yaml.spec.spec.CKV_ARGO_1[6:13]",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
```

So there you have it! A new check will be scanned once your contribution is merged!
