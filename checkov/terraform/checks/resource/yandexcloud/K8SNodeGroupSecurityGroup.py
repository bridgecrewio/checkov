from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE

class K8SNodeGroupSecurityGroup(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure security group is assigned to Kubernetes node group."
        id = "CKV_YC_15"
        supported_resources = ["yandex_kubernetes_node_group"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "instance_template/[0]/network_interface/[0]/security_group_ids"

    def get_expected_value(self):
        return ANY_VALUE
    
check = K8SNodeGroupSecurityGroup()