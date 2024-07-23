from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


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
        supported_resources = ["Microsoft.Search/searchServices", ]
        categories = [CheckCategories.GENERAL_SECURITY, ]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["properties/replicaCount"]

        properties = conf.get("properties", {})
        if not isinstance(properties, dict):
            return CheckResult.FAILED
        replica_count = properties.get("replicaCount")
        if replica_count:
            if not isinstance(replica_count, int):
                return CheckResult.UNKNOWN
            if replica_count >= 2:
                return CheckResult.PASSED

        return CheckResult.FAILED


check = AzureSearchSQLQueryUpdates()
