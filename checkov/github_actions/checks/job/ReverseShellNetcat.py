from typing import Any, Dict, Tuple

from checkov.common.models.enums import CheckResult
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType
import re


class ReverseShellNetcat(BaseGithubActionsCheck):
    def __init__(self):
        name = "Suspicious use of netcat with IP address"
        id = "CKV_GHA_4"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['jobs','jobs.*.steps[]']
        )

    def scan_entity_conf(self, conf: Dict[str, Any]) -> Tuple[CheckResult, Dict[str, Any]]:
        if not isinstance(conf, dict):
            return CheckResult.UNKNOWN, conf
        run = conf.get("run", "")
        if re.search(r'(nc|netcat) (\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})', run):
            return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = ReverseShellNetcat()
