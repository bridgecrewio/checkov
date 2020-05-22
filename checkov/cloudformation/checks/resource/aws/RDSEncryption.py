from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class RDSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_16"
        supported_resources = ['AWS::RDS::DBInstance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration on RDS instance:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
        :param conf: AWS::RDS::DBInstance configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'StorageEncrypted' in conf['Properties'].keys():
                if conf['Properties']['StorageEncrypted'] == True:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = RDSEncryption()
