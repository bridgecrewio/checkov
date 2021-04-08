from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.azure.NSGRulePortAccessRestricted import INTERNET_ADDRESSES
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class NSGRuleUDPAccessRestricted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that UDP Services are restricted from the Internet "
        id = "CKV_AZURE_77"
        supported_resources = ['azurerm_network_security_group', 'azurerm_network_security_rule']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        rule_confs = [conf]
        if 'security_rule' in conf:
            rule_confs = conf['security_rule']
        for rule_conf in rule_confs:
            if 'protocol' in rule_conf and rule_conf['protocol'][0].lower() == 'udp' \
                    and 'direction' in rule_conf and rule_conf['direction'][0].lower() == 'inbound' \
                    and 'access' in rule_conf and rule_conf['access'][0].lower() == 'allow' \
                    and 'source_address_prefix' in rule_conf \
                    and rule_conf['source_address_prefix'][0].lower() in INTERNET_ADDRESSES:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = NSGRuleUDPAccessRestricted()
