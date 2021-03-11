from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class DBInstanceMonitoring(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that that respective logs of Amazon Relational Database Service (Amazon RDS) are enabled"
        id = "CKV_AWS_129"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "monitoring_role_arn"

    def get_expected_value(self):
        return ANY_VALUE

check = DBInstanceMonitoring()
