from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class OSSBucketPublic(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Alibaba Cloud OSS bucket accessible to public"
        id = "CKV_ALI_1"
        supported_resources = ['alicloud_oss_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'acl'

    def get_forbidden_values(self):
        return ["public-read", "public-read-write"]


check = OSSBucketPublic()