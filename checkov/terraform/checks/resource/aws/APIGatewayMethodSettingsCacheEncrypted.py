from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class APIGatewayMethodSettingCacheEncrypted(BaseResourceValueCheck):

    def __init__(self):
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-3(6), NIST.800-53.r5 SC-13, NIST.800-53.r5 SC-28,
        NIST.800-53.r5 SC-28(1), NIST.800-53.r5 SC-7(10), NIST.800-53.r5 SI-7(6)
        """
        name = "Ensure API Gateway method setting caching is set to encrypted"
        id = "CKV_AWS_308"
        supported_resources = ['aws_api_gateway_method_settings']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "settings/[0]/cache_data_encrypted"


check = APIGatewayMethodSettingCacheEncrypted()
