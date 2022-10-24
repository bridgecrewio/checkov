from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class BigTableInstanceEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Big Table Instances are encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_85"
        supported_resources = ['google_bigtable_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'cluster/[0]/kms_key_name'

    def get_expected_value(self):
        return ANY_VALUE


check = BigTableInstanceEncryptedWithCMK()
