import re

from checkov.common.models.enums import CheckResult
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.github_actions.common.shell_injection_list import terms as bad_inputs
from checkov.yaml_doc.enums import BlockType


class DontAllowShellInjection(BaseGithubActionsCheck):
    def __init__(self):
        name = "Ensure run commands are not vulnerable to shell injection"
        id = "CKV_GHA_2"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['jobs','jobs.*.steps[]']
        )

    def scan_entity_conf(self, conf):
        if "run" not in conf:
            return CheckResult.PASSED, conf
        run = conf.get("run", "")
        for term in bad_inputs:
            if re.search(term, run):
                return CheckResult.FAILED, conf

        return CheckResult.PASSED, conf


check = DontAllowShellInjection()
