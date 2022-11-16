from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType


class SuspectCurlInScript(BaseGithubActionsCheck):
    def __init__(self) -> None:
        name = "Suspicious use of curl with secrets"
        id = "CKV_GHA_3"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('jobs', 'jobs.*.steps[]')
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if not isinstance(conf, dict):
            return CheckResult.UNKNOWN, conf
        run = conf.get("run", "")
        if "curl" in run:
            badstuff = ('curl', 'secret')
            lines = run.split("\n")
            for line in lines:
                if all(x in line for x in badstuff):
                    return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = SuspectCurlInScript()
