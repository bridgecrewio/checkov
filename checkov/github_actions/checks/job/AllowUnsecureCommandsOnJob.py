from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult

from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType


class AllowUnsecureCommandsOnJob(BaseGithubActionsCheck):
    def __init__(self) -> None:
        name = "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn't true on environment variables"
        id = "CKV_GHA_1"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('jobs', 'jobs.*.steps[]')
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if not isinstance(conf, dict):
            return CheckResult.UNKNOWN, conf
        if "env" not in conf or not conf["env"]:
            return CheckResult.PASSED, conf
        env_variables = conf.get("env", {})

        if not isinstance(env_variables, dict):
            return CheckResult.UNKNOWN, conf
        if env_variables.get("ACTIONS_ALLOW_UNSECURE_COMMANDS", False):
            return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = AllowUnsecureCommandsOnJob()
