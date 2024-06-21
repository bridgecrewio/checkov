from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class SagemakerDataQualityJobDefinitionEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon Sagemaker Data Quality Job uses KMS to encrypt model artifacts"
        id = "CKV_AWS_367"
        supported_resources = ["AWS::SageMaker::DataQualityJobDefinition"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/DataQualityJobOutputConfig/KmsKeyId'

    def get_expected_value(self):
        return ANY_VALUE


check = SagemakerDataQualityJobDefinitionEncryption()
