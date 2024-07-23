from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceValueCheck


class TKELogAgentEnable(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud TKE clusters enable log agent"
        id = "CKV_TC_6"
        supported_resources = ['tencentcloud_kubernetes_cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "log_agent/enabled"

    def get_expected_value(self) -> bool:
        return True


check = TKELogAgentEnable()
