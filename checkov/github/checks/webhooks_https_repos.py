from __future__ import annotations

import re
from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.github.base_github_configuration_check import BaseGithubCheck
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
        if repository_webhooks_schema.validate(conf):
            for item in conf:
                if isinstance(item, dict):
                    item_config = item.get("config", {})
                    if not item_config:
                        continue
                    url = item_config.get('url', '')
                    insecure_ssl = item_config.get('insecure_ssl', '0')
                    if re.match("^http://", url) or insecure_ssl != '0':
                        return CheckResult.FAILED, item_config
            return CheckResult.PASSED, conf
        return CheckResult.UNKNOWN, conf


check = WebhookHttpsRepo()
