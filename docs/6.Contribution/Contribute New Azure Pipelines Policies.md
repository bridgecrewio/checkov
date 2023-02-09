---
layout: default
published: true
title: Contribute New Azure Pipelines configuration policy
nav_order: 5
---

# Contribute New Azure Pipelines configuration policy

In this example, we'll add support for a new Azure Pipelines configuration check to validate the usage of a version digest.

## Add a Check

Go to `checkov/azure_pipelines/checks/jobs` and add `ContainerDigest.py`:

```python
from __future__ import annotations

from typing import Any

from checkov.azure_pipelines.checks.base_azure_pipelines_check import BaseAzurePipelinesCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class ContainerDigest(BaseAzurePipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure container job uses a version digest"
        id = "CKV_AZUREPIPELINES_2"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.SUPPLY_CHAIN,),
            supported_entities=("jobs", "stages[].jobs[]"),
            block_type=BlockType.ARRAY,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        container = conf.get("container")
        if container and isinstance(container, str):
            if "@" in container:
                return CheckResult.PASSED, conf

            return CheckResult.FAILED, conf

        return CheckResult.UNKNOWN, conf


check = ContainerDigest()
```

### Adding a Test

Create a new folder under `tests/azure_pipelines/checks/jobs` with the name of your check `example_ContainerDigest` for adding example configuration files.
Try to add at least 2 test cases, one passing and one failing. 

`azure-pipelines.yml`:
```yaml
trigger:
- master

resources:
  repositories:
  - repository: AzureDevOps
    type: git
    endpoint: AzureDevOps
    name: AzureDevOps/AzureDevOps

jobs:
- job: RunInContainer
  pool:
    vmImage: 'ubuntu-18.04'

  container: ubuntu@sha256:a0a45bd8c6c4acd6967396366f01f2a68f73406327285edc5b7b07cb1cf073db

  steps:
    - script: printenv
```

Lastly add the test file `test_ContainerDigest.py` to scan the example files.

```python
from pathlib import Path

from checkov.azure_pipelines.runner import Runner
from checkov.azure_pipelines.checks.job.ContainerDigest import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_ContainerDigest"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        f"{test_files_dir}/azure-pipelines.yml.stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_2[22:31]",
    }

    failing_resources = {
        f"{test_files_dir}/azure-pipelines.yml.jobs.jobs.CKV_AZUREPIPELINES_2[32:40]",
        f"{test_files_dir}/azure-pipelines.yml.stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_2[14:22]",
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
