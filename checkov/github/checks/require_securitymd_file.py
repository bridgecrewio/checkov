from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.file_content import schema as file_content_schema
from checkov.json_doc.enums import BlockType


class GithubRequireSecurityMDFile(BaseGithubCheck):
    def __init__(self) -> None:
        # https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
        name = "Ensure all public repositories contain a SECURITY.md file"
        id = "CKV_GITHUB_24"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if 'security_md' in ckv_metadata.get('file_name', ''):
            if file_content_schema.validate(conf):
                return CheckResult.PASSED
            # there was an attempt to find the file, but no file was found in all possible directories.
            return CheckResult.FAILED
        return None


check = GithubRequireSecurityMDFile()
