from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import Dict, List, Any


class AzureSearchSLAIndex(BaseResourceCheck):
    def __init__(self):
        # Cognitive Search services support indexing and querying. Indexing is the process of loading content into
        # the service to make it searchable. Querying is the process where a client searches for content
        # by sending queries to the index.
        # Cognitive Search supports a configurable number of replicas. Having multiple replicas allows queries and
        # index updates to load balance across multiple replicas.
        #
        # To receive a Service Level Agreement (SLA) for Search index updates a minimum of 3 replicas is required.
        name = "Ensure that Azure Search maintains SLA for index updates"
        id = "CKV_AZURE_208"
        supported_resources = ['azurerm_search_service']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("replica_count"):
            count = conf.get("replica_count")[0]
            if count >= 3:
                return CheckResult.PASSED
        self.evaluated_keys = ["replica_count"]
        return CheckResult.FAILED


check = AzureSearchSLAIndex()
