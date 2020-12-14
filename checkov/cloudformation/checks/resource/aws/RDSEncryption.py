from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RDSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_16"
        supported_resources = ['AWS::RDS::DBInstance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
    
    def scan_resource_conf(self, conf):
        # If DB is Aurora then Encryption is set in other resource
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-storageencrypted
        if 'Properties' in conf.keys():
            if 'Engine' in conf['Properties'].keys():
                if 'aurora' in conf['Properties']['Engine']:
                    return CheckResult.UNKNOWN
        # Database is not Aurora; Use base class implementation
        return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'Properties/StorageEncrypted'


check = RDSEncryption()
