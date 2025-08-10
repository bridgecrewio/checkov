from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list


class KMSKeyWildcardPrincipal(BaseResourceCheck):
    def __init__(self):
        name = "Ensure KMS key policy does not contain wildcard (*) principal"
        id = "CKV_AWS_33"
        supported_resources = ['aws_kms_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'policy' not in conf:
            return CheckResult.PASSED
        self.evaluated_keys = ['policy']
        try:
            policy_block = conf['policy'][0]
            if 'Statement' in policy_block:
                self.evaluated_keys = ['policy/[0]/Statement']
                for idx, statement in enumerate(force_list(policy_block['Statement'])):
                    if 'Principal' in statement:
                        principal = statement['Principal']
                        if 'Effect' in statement and statement['Effect'] == 'Deny':
                            continue
                        if 'Condition' in statement:
                            continue
                        if 'AWS' in principal:
                            aws = principal['AWS']
                            if (isinstance(aws, str) and aws == '*') or (isinstance(aws, list) and '*' in aws):
                                idx_evaluated_key = f'[{idx}]/' if isinstance(policy_block['Statement'], list) else ''
                                self.evaluated_keys = [f'policy/[0]/Statement/{idx_evaluated_key}Principal/AWS']
                                return CheckResult.FAILED
                        if (isinstance(principal, str) and principal == '*') or (isinstance(principal, list) and '*' in principal):
                            idx_evaluated_key = f'[{idx}]/' if isinstance(policy_block['Statement'], list) else ''
                            self.evaluated_keys = [f'policy/[0]/Statement/{idx_evaluated_key}Principal']
                            return CheckResult.FAILED
        except Exception:  # nosec
            pass
        return CheckResult.PASSED


check = KMSKeyWildcardPrincipal()
