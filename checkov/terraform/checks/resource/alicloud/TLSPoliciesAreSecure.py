from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class TLSPoliciesAreSecure(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Alibaba Cloud Cypher Policy are secure"
        id = "CKV_ALI_33"
        supported_resources = ['alicloud_slb_tls_cipher_policy']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'tls_versions'

    def get_forbidden_values(self):
        return ["TLSv1.1", "TLSv1.0"]


check = TLSPoliciesAreSecure()
