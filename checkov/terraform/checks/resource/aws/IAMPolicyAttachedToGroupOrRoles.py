from typing import List, Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class IAMPolicyAttachedToGroupOrRoles(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies are attached only to groups or roles (Reducing access management complexity may " \
               "in-turn reduce opportunity for a principal to inadvertently receive or retain excessive privileges.)"
        id = "CKV_AWS_40"
        supported_resources = ('aws_iam_user_policy_attachment', 'aws_iam_user_policy', 'aws_iam_policy_attachment')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        if self.entity_type == "aws_iam_policy_attachment":
            return "users"
        elif self.entity_type in ("aws_iam_user_policy", "aws_iam_user_policy_attachment"):
            return "user"

        return ""

    def get_forbidden_values(self) -> List[Any]:
        return [ANY_VALUE]


check = IAMPolicyAttachedToGroupOrRoles()
