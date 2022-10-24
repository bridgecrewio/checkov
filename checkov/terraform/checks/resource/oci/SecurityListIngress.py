from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class SecurityListIngress(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure VCN has an inbound security list"
        id = "CKV_OCI_16"
        supported_resources = ['oci_core_security_list']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'ingress_security_rules/[0]/protocol'

    def get_expected_value(self):
        return ANY_VALUE


check = SecurityListIngress()
