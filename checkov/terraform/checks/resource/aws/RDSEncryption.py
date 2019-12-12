from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class RDSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_16"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_db_instance:
            https://www.terraform.io/docs/providers/aws/d/db_instance.html
        :param conf: aws_db_instance configuration
        :return: <CheckResult>
        """
        if 'storage_encrypted' in conf.keys():
            key = conf['storage_encrypted'][0]
            if key:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = RDSEncryption()
