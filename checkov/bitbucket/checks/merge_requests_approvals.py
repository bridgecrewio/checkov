from __future__ import annotations

from typing import Any

from checkov.bitbucket.base_bitbucket_configuration_check import BaseBitbucketCheck
from checkov.bitbucket.schemas.branch_restrictions import schema as branch_restrictions_schema
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.json_doc.enums import BlockType


class MergeRequestRequiresApproval(BaseBitbucketCheck):
    def __init__(self) -> None:
        name = "Merge requests should require at least 2 approvals"
        id = "CKV_BITBUCKET_1"
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]] | None:
        if branch_restrictions_schema.validate(conf):
            for value in conf.get("values", []):
                if value.get('kind', '') == 'require_approvals_to_merge':
                    if value.get('value', 0) >= 2:
                        return CheckResult.PASSED, conf
            return CheckResult.FAILED, conf

        return None


check = MergeRequestRequiresApproval()
