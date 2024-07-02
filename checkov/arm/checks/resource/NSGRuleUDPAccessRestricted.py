from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.checks.resource.NSGRulePortAccessRestricted import INTERNET_ADDRESSES
from checkov.arm.base_resource_check import BaseResourceCheck


class NSGRuleUDPAccessRestricted(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that UDP Services are restricted from the Internet "
        id = "CKV_AZURE_77"
        supported_resources = ['Microsoft.Network/networkSecurityGroups',
                               'Microsoft.Network/networkSecurityGroups/securityRules']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> str:
        rule_confs = [conf.get("properties")]
        evaluated_key_prefix = ''
        if 'securityRules' in rule_confs[0]:
            rule_confs = [rule_confs[0]['securityRules'][0]["properties"]]
            self.evaluated_keys = ['securityRules']
            evaluated_key_prefix = 'securityRules/'
        for rule_conf in rule_confs:
            if isinstance(rule_conf, dict):
                # print('\n',rule_conf)
                if 'protocol' in rule_conf and rule_conf['protocol'].lower() == 'udp' \
                        and 'direction' in rule_conf and rule_conf['direction'].lower() == 'inbound' \
                        and 'access' in rule_conf and rule_conf['access'].lower() == 'allow' \
                        and 'sourceAddressPrefix' in rule_conf \
                        and rule_conf['sourceAddressPrefix'].lower() in INTERNET_ADDRESSES:
                    evaluated_key_prefix = f'{evaluated_key_prefix}[{rule_confs.index(rule_conf)}]/' if \
                        evaluated_key_prefix else ''
                    self.evaluated_keys = [f'{evaluated_key_prefix}protocol',
                                           f'{evaluated_key_prefix}direction',
                                           f'{evaluated_key_prefix}access',
                                           f'{evaluated_key_prefix}sourceAddressPrefix']
                    return CheckResult.FAILED
                return CheckResult.PASSED
            return CheckResult.UNKNOWN
        return CheckResult.PASSED


check = NSGRuleUDPAccessRestricted()
