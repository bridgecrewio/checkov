from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSHasSecurityGroup(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no aws_db_security_group resources exist"
        id = "CKV_AWS_198"
        supported_resources = ['aws_db_security_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # this resource should not exist - RDS Security Groups are for use only
        # when working with an RDS instances outside of a VPC.
        return CheckResult.FAILED


check = RDSHasSecurityGroup()
