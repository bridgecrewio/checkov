from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class K8sNodePoolAutoRepair(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure K8s nodepools are set to auto repair"
        id = "CKV_ALI_31"
        supported_resources = ['alicloud_cs_kubernetes_node_pool']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "management/auto_repair"


check = K8sNodePoolAutoRepair()
