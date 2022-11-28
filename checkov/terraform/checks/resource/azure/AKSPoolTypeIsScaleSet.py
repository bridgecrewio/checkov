from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSPoolTypeIsScaleSet(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Azure Kubernetes Cluster (AKS) nodes use scales sets"
        id = "CKV_AZURE_169"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "default_node_pool" in conf.keys():
            self.evaluated_keys = ["default_node_pool/type"]
            pool = conf['default_node_pool'][0]
            if "type" in pool.keys() and isinstance(pool["type"][0], str):
                node_type = pool.get("type")[0]
                if node_type != "VirtualMachineScaleSets":
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = AKSPoolTypeIsScaleSet()
