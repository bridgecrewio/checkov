from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class KMSKeyWildCardPrincipal(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure KMS key policy does not contain wildcard (*) principal"
        id = "CKV_AWS_28"
        supported_resources = ['AWS::KMS::Key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/KeyPolicy/Statement/Principal'

    def scan_resource_conf(self, conf):
        if conf.get('Properties'):
            if conf['Properties'].get('KeyPolicy'):
                policy_block = conf['Properties']['KeyPolicy']
                if 'Statement' in policy_block.keys():
                    for policy_property in policy_block:
                        if policy_property == 'Statement':
                            for policy_statement in policy_block['Statement']:
                                if 'Principal' in policy_statement.keys():
                                    for policy_principal_property in policy_statement['Principal']:
                                        policy_principal_value = policy_statement['Principal'][policy_principal_property]
                                        if str(policy_principal_value) == '*':
                                            return CheckResult.FAILED
        return CheckResult.PASSED


check = KMSKeyWildCardPrincipal()
