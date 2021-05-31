from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import json


class KMSKeyWildcardPrincipal(BaseResourceCheck):

    def __init__(self):
        name = "Ensure KMS key policy does not contain wildcard (*) principal"
        id = "CKV_AWS_33"
        supported_resources = ['aws_kms_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'policy' in conf:
            try:
                policy_block = conf['policy'][0]
                if 'Statement' in policy_block:
                    for statement in force_list(policy_block['Statement']):
                        if 'Principal' in statement:
                            principal = statement['Principal']
                            if 'Effect' in statement and statement['Effect'] == 'Deny':
                                continue
                            if 'AWS' in principal:
                                aws = principal['AWS']
                                if (type(aws) == str and aws == '*') or (type(aws) == list and '*' in aws):
                                    return CheckResult.FAILED
                            if (type(principal) == str and principal == '*') or (type(principal) == list and '*' in principal):
                                 return CheckResult.FAILED
            except:  # nosec
                pass
        return CheckResult.PASSED


check = KMSKeyWildcardPrincipal()
