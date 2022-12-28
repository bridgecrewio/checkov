from typing import Any, List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ShareHostIPC(BaseResourceNegativeValueCheck):

    def __init__(self):
        # CIS-1.3 1.7.3
        # CIS-1.5 5.2.3
        name = "Do not admit containers wishing to share the host IPC namespace"
        id = "CKV_K8S_18"
        supported_resources = ["kubernetes_pod", "kubernetes_pod_v1",
                               "kubernetes_deployment", "kubernetes_deployment_v1"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        if "kubernetes_deployment" == self.entity_type or "kubernetes_deployment_v1" == self.entity_type:
            return "spec/[0]/template/[0]/spec/[0]/host_ipc"
        return "spec/[0]/host_ipc"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = ShareHostIPC()
