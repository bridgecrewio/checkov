from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class IAMPolicyAttachedToGroupOrRoles(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM policies are attached only to groups or roles (Reducing access management complexity may " \
               "in-turn reduce opportunity for a principal to inadvertently receive or retain excessive privileges.) "
        id = "CKV_AWS_40"
        supported_resources = ['aws_iam_user_policy_attachment', 'aws_iam_user_policy', 'aws_iam_policy_attachment']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'user' in conf.keys() or 'users' in conf.keys():
            return CheckResult.FAILED
        return CheckResult.PASSED

check = IAMPolicyAttachedToGroupOrRoles()
