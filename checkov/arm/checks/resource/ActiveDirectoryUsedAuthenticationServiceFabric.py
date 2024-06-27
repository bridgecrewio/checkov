from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class ActiveDirectoryUsedAuthenticationServiceFabric(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensures that Active Directory is used for authentication for Service Fabric"
        id = "CKV_AZURE_126"
        supported_resources = ("Microsoft.ServiceFabric/clusters")
        categories = (CheckCategories.GENERAL_SECURITY)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources)

    def get_inspected_key(self):
        return "azureActiveDirectory/tenantId"

    def get_expected_value(self):
        return ANY_VALUE


check = ActiveDirectoryUsedAuthenticationServiceFabric()
