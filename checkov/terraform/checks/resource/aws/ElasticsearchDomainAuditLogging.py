from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ElasticsearchDomainAuditLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Elasticsearch Domain Audit Logging is enabled"
        id = "CKV_AWS_317"
        supported_resources = ("aws_elasticsearch_domain", "aws_opensearch_domain")
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        options = conf.get("log_publishing_options")
        if options and isinstance(options, list):
            for option in options:
                if isinstance(option, dict):
                    log_type = option.get("log_type")
                    if log_type and isinstance(log_type, list) and log_type[0] == "AUDIT_LOGS":
                        enabled = option.get("enabled")
                        if enabled and isinstance(enabled, list) and enabled[0]:
                            return CheckResult.PASSED

        return CheckResult.FAILED


check = ElasticsearchDomainAuditLogging()
