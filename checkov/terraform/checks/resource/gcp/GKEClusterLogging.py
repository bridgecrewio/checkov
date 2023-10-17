from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class GKEClusterLogging(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Stackdriver Logging is set to Enabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_1"
        supported_resources = ("google_container_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logging_service"

    def get_forbidden_values(self):
        return "none"


check = GKEClusterLogging()
