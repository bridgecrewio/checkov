from typing import List, Any

from checkov.cloudformation.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class IAMPolicyAttachedToGroupOrRoles(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure IAM policies are attached only to groups or roles (Reducing access management complexity may " \
               "in-turn reduce opportunity for a principal to inadvertently receive or retain excessive privileges.)"
        id = "CKV_AWS_40"
        supported_resources = ['AWS::IAM::Policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for users attached to an IAM policy
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html
        :param conf: aws_iam_policy
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            props_conf = conf['Properties']
            if 'Users' in props_conf.keys():
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_inspected_key(self) -> str:
        return "Properties/Users"

    def get_forbidden_values(self) -> List[Any]:
        return ANY_VALUE


check = IAMPolicyAttachedToGroupOrRoles()
