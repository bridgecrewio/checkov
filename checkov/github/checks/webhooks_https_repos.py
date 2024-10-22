from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.github.base_github_configuration_check import BaseGithubCheck, HTTP
from checkov.github.schemas.repository_webhooks import schema as repository_webhooks_schema
from checkov.json_doc.enums import BlockType


class WebhookHttpsRepo(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure GitHub repository webhooks are using HTTPS"
        id = "CKV_GITHUB_7"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]] | None:  # type:ignore[override]
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if 'repository_webhooks' in ckv_metadata.get('file_name', ''):
            if repository_webhooks_schema.validate(conf):
                for item in conf:
                    if isinstance(item, dict):
                        item_config = item.get("config", {})
                        if not item_config:
                            continue
                        url = item_config.get('url', '')
                        insecure_ssl = item_config.get('insecure_ssl', '0')
                        if url.startswith(HTTP):
                            return CheckResult.FAILED, item_config
                        if insecure_ssl != '0':
                            return CheckResult.FAILED, item_config
                return CheckResult.PASSED, conf
        return CheckResult.UNKNOWN, conf


check = WebhookHttpsRepo()
