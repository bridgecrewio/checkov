from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class OSSBucketVersioning(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure OSS bucket has versioning enabled"
        id = "CKV_ALI_10"
        supported_resources = ['alicloud_oss_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'versioning/[0]/status'

    def get_expected_value(self):
        return 'Enabled'


check = OSSBucketVersioning()
