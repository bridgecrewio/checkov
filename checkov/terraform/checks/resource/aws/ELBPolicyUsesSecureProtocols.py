
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ELBPolicyUsesSecureProtocols(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ELB Policy uses only secure protocols"
        id = "CKV_AWS_213"
        supported_resources = ['aws_load_balancer_policy']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        self.evaluated_keys = ['policy_attribute']
        policies = conf.get('policy_attribute')
        for policy in policies:
            name = policy.get("name")[0]
            if name in ("Protocol-SSLv3", "Protocol-TLSv1", "Protocol-TLSv1.1"):
                if policy.get("value")[0]:
                    return CheckResult.FAILED
            if name == "Reference-Security-Policy":
                value = policy.get("value")[0]
                if value in ("ELBSecurityPolicy-2016-08", "ELBSecurityPolicy-TLS-1-1-2017-01",
                             "ELBSecurityPolicy-2015-05", "ELBSecurityPolicy-2015-03", "ELBSecurityPolicy-2015-02",
                             "ELBSecurityPolicy-TLS-1-0-2015-04", "ELBSecurityPolicy-2014-10",
                             "ELBSecurityPolicy-Default", "ELBSecurityPolicy-2014-01"):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = ELBPolicyUsesSecureProtocols()
