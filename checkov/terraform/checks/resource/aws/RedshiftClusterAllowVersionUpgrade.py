from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.enums import CheckResult


class RedshiftClusterAllowVersionUpgrade(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensured that redshift cluster allowing version upgrade by default"
        id = "CKV_AWS_141"
        supported_resources = ['aws_redshift_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "allow_version_upgrade"


check = RedshiftClusterAllowVersionUpgrade()
