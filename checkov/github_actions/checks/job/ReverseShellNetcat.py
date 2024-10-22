from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType
import re

NETCAT_IP_PATTERN = re.compile(r'(nc|netcat) (\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})')


class ReverseShellNetcat(BaseGithubActionsCheck):
    def __init__(self) -> None:
        name = "Suspicious use of netcat with IP address"
        id = "CKV_GHA_4"
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
        if re.search(NETCAT_IP_PATTERN, run):
            return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf


check = ReverseShellNetcat()
