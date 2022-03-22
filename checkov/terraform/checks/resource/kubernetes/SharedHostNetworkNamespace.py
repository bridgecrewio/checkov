from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SharedHostNetworkNamespace(BaseResourceValueCheck):

    def __init__(self):
        # CIS-1.3 1.7.4
        # CIS-1.5 5.2.4
        name = "Do not admit containers wishing to share the host network namespace"
        id = "CKV_K8S_19"
        supported_resources = ["kubernetes_pod"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "spec/[0]/host_network"

    def get_expected_value(self) -> Any:
        return False


check = SharedHostNetworkNamespace()
