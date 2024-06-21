from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class SagemakerDataQualityJobDefinitionTrafficEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon Sagemaker Data Quality Job encrypts all communications between instances used for monitoring jobs"
        id = "CKV_AWS_369"
        supported_resources = ['aws_sagemaker_data_quality_job_definition']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "network_config/[0]/enable_inter_container_traffic_encryption"


check = SagemakerDataQualityJobDefinitionTrafficEncryption()
