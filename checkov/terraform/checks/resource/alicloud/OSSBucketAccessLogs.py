from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class OSSBucketAccessLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the OSS bucket has access logging enabled"
        id = "CKV_ALI_12"
        supported_resources = ['alicloud_oss_bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'logging'

    def get_expected_value(self):
        return ANY_VALUE


check = OSSBucketAccessLogs()