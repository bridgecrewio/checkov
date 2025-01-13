from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSNodePublicIpDisabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AKS cluster nodes do not have public IP addresses"
        id = "CKV_AZURE_143"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'default_node_pool' in conf:
            default_node_pool = conf['default_node_pool'][0]
            if isinstance(default_node_pool, dict):
                if default_node_pool.get('enable_node_public_ip') == [True] or default_node_pool.get('node_public_ip_enabled') == [True]:
                    return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['default_node_pool/[0]/enable_node_public_ip', 'default_node_pool/[0]/node_public_ip_enabled']


check = AKSNodePublicIpDisabled()
