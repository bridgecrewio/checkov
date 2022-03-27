from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories

#
class MWAAWebserverLogsEnabled(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure MWAA environment has webserver logs enabled"
        id = "CKV_AWS_244"
        supported_resources = ['aws_mwaa_environment']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logging_configuration/[0]/webserver_logs/[0]/enabled"


check = MWAAWebserverLogsEnabled()
