from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.dal import CKV_GITHUB_DEFAULT
from checkov.json_doc.enums import BlockType


class GithubIssueDeletionIsLimited(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure issue deletion is limited to specific users"
        # see https://docs.github.com/en/repositories/creating-and-managing-repositories/deleting-a-repository
        # in GitHub only owners can remove a repo, and that's what the check require
        id = "CKV_GITHUB_25"
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        if CKV_GITHUB_DEFAULT in conf:
            return CheckResult.PASSED
        return None


check = GithubIssueDeletionIsLimited()
