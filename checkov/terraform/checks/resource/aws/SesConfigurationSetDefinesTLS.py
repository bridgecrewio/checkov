from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class SesConfigurationSetDefinesTLS(BaseResourceValueCheck):

    def __init__(self) -> None:
        name = "Ensure SES Configuration Set enforces TLS usage"
        id = "CKV_AWS_365"
        supported_resources = ['aws_ses_configuration_set']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "delivery_options/[0]/tls_policy"

    def get_expected_value(self) -> str:
        return "Require"


check = SesConfigurationSetDefinesTLS()
