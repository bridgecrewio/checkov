from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GKEBinaryAuthorization(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure use of Binary Authorization"
        id = "CKV_GCP_66"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'enable_binary_authorization'

check = GKEBinaryAuthorization()
