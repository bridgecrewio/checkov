from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LaunchTemplateMetadataHop(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2, NIST.800-53.r5 CM-2(2)
        Auto Scaling group launch configuration should not have a metadata response hop limit greater than 1
        """
        name = "Ensure Launch template should not have a metadata response hop limit greater than 1"
        id = "CKV_AWS_341"
        supported_resources = ("aws_launch_configuration", "aws_launch_template")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "metadata_options/[0]/http_put_response_hop_limit"

    def get_expected_value(self):
        return 1


check = LaunchTemplateMetadataHop()
