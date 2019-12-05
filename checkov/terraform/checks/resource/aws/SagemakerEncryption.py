from checkov.terraform.models.enums import ScanResult, ScanCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class SagemakerEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Sagemaker is securely encrypted at rest"
        scan_id = "BC_AWS_SAGEMAKER_1"
        supported_resources = ['aws_sagemaker_notebook_instance']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_sagemaker_notebook_instance:
            https://www.terraform.io/docs/providers/aws/r/sagemaker_notebook_instance.html
        :param conf: aws_sagemaker_notebook_instance configuration
        :return: <ScanResult>
        """
        if 'kms_key_id' in conf.keys():
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = SagemakerEncryption()
