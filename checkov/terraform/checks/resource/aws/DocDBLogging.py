from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DocDBLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure DocDB Logging is enabled"
        id = "CKV_AWS_85"
        supported_resources = ['aws_docdb_cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "enabled_cloudwatch_logs_exports"

    def get_expected_value(self):
        return ANY_VALUE


check = DocDBLogging()
