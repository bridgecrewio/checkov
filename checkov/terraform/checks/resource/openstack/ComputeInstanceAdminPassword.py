from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.consts import ANY_VALUE


class ComputeInstanceAdminPassword(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that instance does not use basic credentials"
        id = "CKV_OPENSTACK_4"
        supported_resources = ['openstack_compute_instance_v2']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return 'admin_pass'

    def get_forbidden_values(self):
        return [ANY_VALUE]


check = ComputeInstanceAdminPassword()
