from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class CodeBuildPrivilegedMode(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-2(1), NIST.800-53.r5 AC-3, NIST.800-53.r5 AC-3(15), NIST.800-53.r5 AC-3(7),
        NIST.800-53.r5 AC-5, NIST.800-53.r5 AC-6, NIST.800-53.r5 AC-6(10), NIST.800-53.r5 AC-6(2)
        CodeBuild project environments should not have privileged mode enabled
        """
        name = "Ensure CodeBuild project environments do not have privileged mode enabled"
        id = "CKV_AWS_316"
        supported_resources = ['aws_codebuild_project']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "environment/[0]/privileged_mode"

    def get_forbidden_values(self):
        return [True]


check = CodeBuildPrivilegedMode()
