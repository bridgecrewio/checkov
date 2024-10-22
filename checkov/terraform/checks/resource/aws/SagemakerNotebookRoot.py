
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SagemakerNotebookRoot(BaseResourceValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-2(1), NIST.800-53.r5 AC-3(15), NIST.800-53.r5 AC-3(7), NIST.800-53.r5 AC-6, NIST.800-53.r5
        AC-6(10), NIST.800-53.r5 AC-6(2)
        """
        name = "Ensure SageMaker Users should not have root access to SageMaker notebook instances"
        id = "CKV_AWS_307"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return 'root_access'

    def get_expected_value(self):
        return "Disabled"


check = SagemakerNotebookRoot()
