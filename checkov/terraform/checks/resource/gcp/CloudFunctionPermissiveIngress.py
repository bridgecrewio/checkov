from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudFunctionPermissiveIngress(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure GCP Cloud Function is not configured with overly permissive Ingress setting"
        id = "CKV_GCP_124"
        supported_resources = ("google_cloudfunctions_function", "google_cloudfunctions2_function")
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        if self.entity_type == "google_cloudfunctions_function":
            return "ingress_settings"
        else:
            return "service_config/[0]/ingress_settings/[0]"

    def get_expected_values(self) -> List[Any]:
        return ["ALLOW_INTERNAL_AND_GCLB", "ALLOW_INTERNAL_ONLY"]


check = CloudFunctionPermissiveIngress()
