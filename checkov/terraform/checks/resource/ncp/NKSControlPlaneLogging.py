from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class NKSControlPlaneLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure NKS control plane logging enabled for all log types"
        id = "CKV_NCP_22"
        supported_resources = ('ncloud_nks_cluster',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'log/0/audit/0'


check = NKSControlPlaneLogging()
