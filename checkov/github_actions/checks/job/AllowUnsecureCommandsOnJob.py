from checkov.common.models.enums import CheckResult

from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType


class AllowUnsecureCommandsOnJob(BaseGithubActionsCheck):
    def __init__(self):
        name = "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn't true on environment variables"
        id = "CKV_GHA_1"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['jobs', 'jobs.*.steps[]']
        )

    def scan_entity_conf(self, conf):
        if "env" not in conf:
            return CheckResult.PASSED, conf
        env_variables = conf.get("env", {})
        if env_variables.get("ACTIONS_ALLOW_UNSECURE_COMMANDS", False):
            return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = AllowUnsecureCommandsOnJob()
