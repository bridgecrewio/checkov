from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class OSSBucketEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure OSS bucket is encrypted with Customer Master Key"
        id = "CKV_ALI_6"
        supported_resources = ['alicloud_oss_bucket']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'server_side_encryption_rule/[0]/kms_master_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = OSSBucketEncryptedWithCMK()
