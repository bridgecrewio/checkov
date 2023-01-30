from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureSearchSQLQueryUpdates(BaseResourceCheck):
    def __init__(self) -> None:
        # Cognitive Search services support indexing and querying. Indexing is the process of loading content
        # into the service to make it searchable. Querying is the process where a client searches for content
        # by sending queries to the index.
        # Cognitive Search supports a configurable number of replicas.
        # Having multiple replicas allows queries and index updates to load balance across multiple replicas.
        # To receive a Service Level Agreement (SLA) for Search index queries a minimum of 2 replicas is required.
        name = "Ensure that Azure Cognitive Search maintains SLA for search index queries"
        id = "CKV_AZURE_209"
        supported_resources = ("azurerm_search_service",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["replica_count"]

        replica_count = conf.get("replica_count")
        if replica_count and isinstance(replica_count, list):
            if not isinstance(replica_count[0], int):
                return CheckResult.UNKNOWN
            if replica_count[0] >= 2:
                return CheckResult.PASSED

        return CheckResult.FAILED


check = AzureSearchSQLQueryUpdates()
