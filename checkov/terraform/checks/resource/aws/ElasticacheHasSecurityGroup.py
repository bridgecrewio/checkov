from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ElasticacheHasSecurityGroup(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no aws_elasticache_security_group resources exist"
        id = "CKV_AWS_196"
        supported_resources = ['aws_elasticache_security_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # this resource should not exist - ElastiCache Security Groups are for use only
        # when working with an ElastiCache cluster outside of a VPC.
        return CheckResult.FAILED


check = ElasticacheHasSecurityGroup()
