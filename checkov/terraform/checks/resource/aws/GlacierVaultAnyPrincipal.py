import json
import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from policyuniverse.policy import Policy
from typing import List

DATA_TO_JSON_PATTERN = re.compile(r"\$?\{?(.+?)(?=.json).json\}?")


class GlacierVaultAnyPrincipal(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Glacier Vault access policy is not public by only allowing specific services or principals to access it"
        id = "CKV_AWS_167"
        supported_resources = ['aws_glacier_vault']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'access_policy' not in conf:
            return CheckResult.PASSED
        policy_obj = conf['access_policy'][0]
        if isinstance(policy_obj, str):
            if re.match(DATA_TO_JSON_PATTERN, policy_obj):
                return CheckResult.UNKNOWN
            else:
                try:
                    policy_obj = json.loads(policy_obj)
                except Exception:
                    return CheckResult.UNKNOWN
        try:
            policy = Policy(policy_obj)
        except TypeError:
            return CheckResult.UNKNOWN
        if policy.is_internet_accessible():
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['access_policy']


check = GlacierVaultAnyPrincipal()
