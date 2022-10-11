from typing import List, Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class IAMUserNotUsedForAccess(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure access is controlled through SSO and not AWS IAM defined users"
        id = "CKV_AWS_273"
        supported_resources = ('aws_iam_user')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        if self.entity_type == "aws_iam_user":
            return "name"

        return ""

    def get_forbidden_values(self) -> List[Any]:
        return [ANY_VALUE]


check = IAMUserNotUsedForAccess()
