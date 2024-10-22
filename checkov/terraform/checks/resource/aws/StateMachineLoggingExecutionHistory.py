from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class StateMachineLoggingExecutionHistory(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure State Machine has execution history logging enabled"
        id = "CKV_AWS_285"
        supported_resources = ['aws_sfn_state_machine']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logging_configuration/[0]/include_execution_data"


check = StateMachineLoggingExecutionHistory()
