from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.repository_collaborators import schema as repository_collaborators_schema
from checkov.json_doc.enums import BlockType


class GithubRepositoryCollaborators(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure 2 admins are set for each repository"
        id = "CKV_GITHUB_9"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:  # type:ignore[override]
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if 'repository_collaborators' in ckv_metadata.get('file_name', ''):
            if conf and repository_collaborators_schema.validate(conf):
                admin_collaborators = 0
                for item in conf:
                    if isinstance(item, dict):
                        permissions = item.get("permissions", {})
                        admin = permissions.get('admin', False)
                        if admin:
                            admin_collaborators += 1
                if admin_collaborators >= 2:
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = GithubRepositoryCollaborators()
