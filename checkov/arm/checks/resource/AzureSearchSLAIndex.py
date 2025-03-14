from __future__ import annotations

from typing import Any, Dict

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureSearchSLAIndex(BaseResourceCheck):
    def __init__(self) -> None:
        # Cognitive Search services support indexing and querying. Indexing is the process of loading content into
        # the service to make it searchable. Querying is the process where a client searches for content
        # by sending queries to the index.
        # Cognitive Search supports a configurable number of replicas. Having multiple replicas allows queries and
        # index updates to load balance across multiple replicas.
        #
        # To receive a Service Level Agreement (SLA) for Search index updates a minimum of 3 replicas is required.
        name = "Ensure that Azure Cognitive Search maintains SLA for index updates"
        id = "CKV_AZURE_208"
        supported_resources = ["Microsoft.Search/searchServices", ]
        categories = [CheckCategories.GENERAL_SECURITY, ]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get("properties", {})
        self.evaluated_keys = ["properties"]
        if not isinstance(properties, dict):
            return CheckResult.FAILED
        replica_count = properties.get("replicaCount")
        if replica_count and isinstance(replica_count, int):
            if replica_count >= 3:
                return CheckResult.PASSED
            else:
                self.evaluated_keys = ["properties/replicaCount"]
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED


check = AzureSearchSLAIndex()
