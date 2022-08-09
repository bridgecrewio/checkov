import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github.schemas.org_webhooks import schema as org_webhooks_schema
from checkov.github.schemas.repository_webhooks import schema as repository_webhooks_schema
from checkov.json_doc.enums import BlockType


class WebhookHttps(BaseGithubCheck):
    def __init__(self):
        name = "Ensure GitHub organization and repository webhooks are using HTTPS"
        id = "CKV_GITHUB_7"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf):

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
        if org_webhooks_schema.validate(conf):
            for item in conf:
                if isinstance(item, dict):
                    item_config = item.get("config", {})
                    if not item_config:
                        continue
                    url = item_config.get('url', '')
                    insecure_ssl = item_config.get('insecure_ssl', '0')
                    secret = item_config.get('secret', '')
                    if re.match("^http://", url) or insecure_ssl != '0' and secret != '********':  # nosec
                        return CheckResult.FAILED, item_config
        if org_webhooks_schema.validate(conf) or repository_webhooks_schema.validate(conf):
            return CheckResult.PASSED, conf


check = WebhookHttps()
