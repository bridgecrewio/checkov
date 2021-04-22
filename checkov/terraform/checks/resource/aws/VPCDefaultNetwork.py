from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class VPCDefaultNetwork(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no default VPC is planned to be provisioned"
        id = "CKV_AWS_148"
        supported_resources = ['aws_default_vpc']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Checks if there is any attempt to create a default VPC configuration :
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/default_vpc
            :param conf: aws_default_vpc configuration
            :return: <CheckResult>
        """
    
        return CheckResult.FAILED
check = VPCDefaultNetwork()


