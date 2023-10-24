from __future__ import annotations

from typing import Any


from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.org_members import schema as org_members
from checkov.json_doc.enums import BlockType

MAX_ADMIN_COUNT = 3


class GithubMinimumAdminsInOrganization(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure minimum admins are set for the organization"
        id = "CKV_GITHUB_26"
        categories = (CheckCategories.SUPPLY_CHAIN, )
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if 'org_admins' in ckv_metadata.get('file_name', ''):
            if org_members.validate(conf):
                if len(conf) <= MAX_ADMIN_COUNT:
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = GithubMinimumAdminsInOrganization()
