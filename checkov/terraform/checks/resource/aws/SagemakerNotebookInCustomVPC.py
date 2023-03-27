from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SagemakerNotebookInCustomVPC(BaseResourceValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-21, NIST.800-53.r5 AC-3, NIST.800-53.r5 AC-3(7), NIST.800-53.r5 AC-4, NIST.800-53.r5 AC-4(21),
        NIST.800-53.r5 AC-6, NIST.800-53.r5 SC-7, NIST.800-53.r5 SC-7(11), NIST.800-53.r5 SC-7(16),
        NIST.800-53.r5 SC-7(20), NIST.800-53.r5 SC-7(21), NIST.800-53.r5 SC-7(3), NIST.800-53.r5 SC-7(4),
        NIST.800-53.r5 SC-7(9)
        """
        name = "Ensure SageMaker notebook instances should be launched into a custom VPC"
        id = "CKV_AWS_306"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'subnet_id'

    def get_expected_value(self):
        return ANY_VALUE


check = SagemakerNotebookInCustomVPC()
