from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class EFSAccessPointRoot(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-6(10)
        EFS access points should enforce a root directory (avoiding root / default)
        """
        name = "EFS access points should enforce a root directory"
        id = "CKV_AWS_329"
        supported_resources = ['aws_efs_access_point']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "root_directory/[0]/path"

    def get_forbidden_values(self):
        return "/"


check = EFSAccessPointRoot()
