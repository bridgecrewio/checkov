from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ALBACLIsUnrestricted(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Alibaba ALB ACL does not restrict Access"
        id = "CKV_ALI_29"
        supported_resources = ['alicloud_alb_acl_entry_attachment']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'entry'

    def get_forbidden_values(self):
        return ["0.0.0.0/0"]


check = ALBACLIsUnrestricted()
