import json

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import is_json
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import List, Any


class ECRPolicy(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure ECR policy is not set to public"
        id = "CKV_AWS_32"
        supported_resources = ['aws_ecr_repository_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'policy/[0]/Statement/[0]/Principal'

    def get_forbidden_values(self) -> List[Any]:
        return ['*']


check = ECRPolicy()
