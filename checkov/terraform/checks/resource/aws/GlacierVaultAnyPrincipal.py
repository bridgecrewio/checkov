import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from policyuniverse.policy import Policy

DATA_TO_JSON_PATTERN = r"\$?\{?(.+?)(?=.json).json\}?"

class GlacierVaultAnyPrincipal(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Glacier Vault access policy is not public by only allowing specific services or principals to access it"
        id = "CKV_AWS_167"
        supported_resources = ['aws_glacier_vault']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'access_policy' in conf:
            policy_obj = conf['access_policy'][0]
            if isinstance(policy_obj, str):
                if re.match(DATA_TO_JSON_PATTERN, policy_obj):
                    return CheckResult.UNKNOWN
            policy = Policy(policy_obj)
            if policy.is_internet_accessible():
                return CheckResult.FAILED
        return CheckResult.PASSED


check = GlacierVaultAnyPrincipal()
