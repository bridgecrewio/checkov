from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SagemakerEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Sagemaker is securely encrypted at rest"
        id = "CKV_AWS_22"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_sagemaker_notebook_instance:
            https://www.terraform.io/docs/providers/aws/r/sagemaker_notebook_instance.html
        :param conf: aws_sagemaker_notebook_instance configuration
        :return: <CheckResult>
        """
        if 'kms_key_id' in conf.keys():
                return CheckResult.PASSED
        return CheckResult.FAILED


check = SagemakerEncryption()
