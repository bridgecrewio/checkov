from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class TransferServerPubliclyAccessible(BaseResourceCheck):

    def __init__(self):
        name = "TransferServer should not have public access"
        id = "CKV_AWS_164"
        supported_resources = ['AWS::Transfer::Server']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates EndpointType for TransferServer
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-transfer-server.html#cfn-transfer-server-endpointtype
        """

        if 'Properties' in conf.keys():
            if 'EndpointType' in conf['Properties'].keys():
                if conf['Properties']['EndpointType'] == "PUBLIC":
                    return CheckResult.FAILED
                elif conf['Properties']['EndpointType'] in ('VPC', 'VPC_ENDPOINT'):
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        return CheckResult.FAILED   # if we have not mention the 'EndpointType' then by default it uses 'PUBLIC' endpoint.

check = TransferServerPubliclyAccessible()
