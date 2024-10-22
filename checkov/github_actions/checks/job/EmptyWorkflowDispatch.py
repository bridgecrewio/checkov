from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType


class EmptyWorkflowDispatch(BaseGithubActionsCheck):
    def __init__(self) -> None:
        name = "The build output cannot be affected by user parameters other than the build entry point and the " \
               "top-level source location. GitHub Actions workflow_dispatch inputs MUST be empty. "
        id = "CKV_GHA_7"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.OBJECT,
            supported_entities=('on',)
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if isinstance(conf, list):
            for sub_conf in conf:
                if sub_conf == "workflow_dispatch":
                    return CheckResult.PASSED, sub_conf
            return CheckResult.UNKNOWN, {}

        if isinstance(conf, str):
            if conf == "workflow_dispatch":
                return CheckResult.PASSED, conf
            else:
                return CheckResult.UNKNOWN, conf

        workflow_dispatch = conf.get("workflow_dispatch")
        if isinstance(workflow_dispatch, dict):
            workflow_dispatch_inputs = workflow_dispatch.get("inputs", {})
            if workflow_dispatch_inputs:
                return CheckResult.FAILED, workflow_dispatch_inputs
        return CheckResult.PASSED, conf


check = EmptyWorkflowDispatch()
