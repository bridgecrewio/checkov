from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class SagemakerDataQualityJobDefinitionVolumeEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon Sagemaker Data Quality Job uses KMS to encrypt data on attached storage volume"
        id = "CKV_AWS_368"
        supported_resources = ['aws_sagemaker_data_quality_job_definition']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "job_resources/[0]/cluster_config/[0]/volume_kms_key_id"

    def get_expected_value(self):
        return ANY_VALUE


check = SagemakerDataQualityJobDefinitionVolumeEncryption()
