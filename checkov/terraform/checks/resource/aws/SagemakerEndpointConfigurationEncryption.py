from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SagemakerEndpointConfigurationEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Sagemaker Endpoint is securely encrypted at rest"
        id = "CKV_AWS_98"
        supported_resources = ['aws_sagemaker_endpoint_configuration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'kms_key_arn' in conf.keys():
                return CheckResult.PASSED
        return CheckResult.FAILED


check = SagemakerEndpointConfigurationEncryption()
