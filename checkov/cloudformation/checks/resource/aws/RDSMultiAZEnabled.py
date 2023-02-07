from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RDSMultiAZEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that RDS instances have Multi-AZ enabled"
        id = "CKV_AWS_157"
        supported_resources = ("AWS::RDS::DBInstance",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Aurora is replicated across all AZs and doesn't require MultiAZ to be set
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbinstance.html#cfn-rds-dbinstance-multiaz
        if 'Properties' in conf.keys():
            if 'Engine' in conf['Properties'].keys():
                if 'aurora' in conf['Properties']['Engine']:
                    return CheckResult.UNKNOWN
        # Database is not Aurora; Use base class implementation
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return 'Properties/MultiAZ'


check = RDSMultiAZEnabled()
