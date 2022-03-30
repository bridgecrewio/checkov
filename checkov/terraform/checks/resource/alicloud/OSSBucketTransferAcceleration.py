from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class OSSBucketTransferAcceleration(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure OSS bucket has transfer Acceleration enabled"
        id = "CKV_ALI_11"
        supported_resources = ['alicloud_oss_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'transfer_acceleration/[0]/enabled'


check = OSSBucketTransferAcceleration()
