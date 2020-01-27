from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class IAMPolicyAttachedToGroupOrRoles(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM policies are attached only to groups or roles (Reducing access management complexity may " \
               "in-turn reduce opportunity for a principal to inadvertently receive or retain excessive privileges.) "
        id = "CKV_AWS_40"
        supported_resources = ['aws_iam_user_policy_attachment', 'aws_iam_user_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # fail if this kind of resources is identified - since policies should only be attached to groups and roles
        return CheckResult.FAILED


check = IAMPolicyAttachedToGroupOrRoles()
