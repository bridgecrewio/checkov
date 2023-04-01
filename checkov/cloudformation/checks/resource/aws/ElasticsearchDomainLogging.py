from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ElasticsearchDomainLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Elasticsearch Domain Logging is enabled"
        id = "CKV_AWS_84"
        supported_resources = ("AWS::Elasticsearch::Domain", "AWS::OpenSearchService::Domain")
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("Properties")
        if properties:
            options = properties.get("LogPublishingOptions")
            if options:
                for option_conf in options.values():
                    if isinstance(option_conf, dict) and option_conf.get("Enabled"):
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticsearchDomainLogging()
