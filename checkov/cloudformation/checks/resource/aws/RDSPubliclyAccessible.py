from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class RDSPubliclyAccessible(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS bucket is not public accessible"
        id = "CKV_AWS_17"
        supported_resources = ['AWS::RDS::DBInstance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for publicy accessible configuration on RDS instance:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
        :param conf: AWS::RDS::DBInstance configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'PubliclyAccessible' in conf['Properties'].keys():
                if conf['Properties']['PubliclyAccessible'] == True:
                    return CheckResult.FAILED
        return CheckResult.PASSED

check = RDSPubliclyAccessible()
