from typing import List, Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class IAMOrganizationElevatedMembers(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure organization member does not have elevated access."
        id = "CKV_YC_21"
        categories = (CheckCategories.IAM,)
        supported_resources = (
            "yandex_organizationmanager_organization_iam_binding",
            "yandex_organizationmanager_organization_iam_member",
        )
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "role"

    def get_forbidden_values(self) -> List[Any]:
        return ["admin", "editor", "organization-manager.organizations.owner", "organization-manager.admin"]


check = IAMOrganizationElevatedMembers()
