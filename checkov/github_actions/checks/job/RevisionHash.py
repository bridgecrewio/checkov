from __future__ import annotations

import re
from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck
from checkov.yaml_doc.enums import BlockType

# Matches @ followed by a 40-character SHA-1 commit hash with optional trailing comment
COMMIT_ID_PATTERN = re.compile(r"@[0-9a-f]{40}\s*(#.*)?$")


class RevisionHash(BaseGithubActionsCheck):
    def __init__(self) -> None:
        name = "Ensure GitHub Action sources use a commit hash"
        id = "CKV_GHA_8"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('jobs', 'jobs.*.steps[]')
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any] | None]:
        if not isinstance(conf, dict):
            return CheckResult.UNKNOWN, conf
        uses = conf.get("uses", None)

        if uses is None or re.search(COMMIT_ID_PATTERN, uses):
            return CheckResult.PASSED, conf

        return CheckResult.FAILED, conf


check = RevisionHash()
