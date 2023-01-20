from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories

class RDSMultiAZEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that RDS instances have Multi-AZ enabled"
        id = "CKV_AWS_157"
        supported_resources = ['AWS::RDS::DBInstance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        properties = conf.get("Properties")
        aurora = "aurora"
        if properties:
            engine = properties.get("Engine")
            # Aurora is replicated across all AZs and doesn't require MultiAZ to be set
            if engine and engine in aurora:
                return CheckResult.PASSED
            value = properties.get("MultiAZ")
            if isinstance(value, bool):
                value = str(value).lower()
            if value == "true":
                return CheckResult.PASSED
        return CheckResult.FAILED

check = RDSMultiAZEnabled()
