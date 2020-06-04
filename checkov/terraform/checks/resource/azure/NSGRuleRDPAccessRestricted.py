from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import re

PORT_RANGE = re.compile('\d+-\d+')


class NSGRuleRDPAccessRestricted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that RDP access is restricted from the internet"
        id = "CKV_AZURE_9"
        supported_resources = ['azure_security_group_rule', 'azurerm_network_security_rule']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def is_3389_in_range(self, conf):
        ports = force_list(conf['destination_port_range'][0])
        for range in ports:
            if re.match(PORT_RANGE, range):
                start, end = int(range.split('-')[0]), int(range.split('-')[1])
                if start <= 3389 <= end:
                    return True
            if range in ['3389', '*']:
                return True
        return False

    def scan_resource_conf(self, conf):
        if 'access' in conf and conf['access'][0] == "Allow":
            if 'direction' in conf and conf['direction'][0] == "Inbound":
                if 'protocol' in conf and conf['protocol'][0] == 'TCP':
                    if 'destination_port_range' in conf and self.is_3389_in_range(conf):
                        if 'source_address_prefix' in conf and conf['source_address_prefix'][0] in ["*", "0.0.0.0",
                                                                                             "<nw>/0", "/0",
                                                                                             "internet", "any"]:
                            return CheckResult.FAILED
        return CheckResult.PASSED




check = NSGRuleRDPAccessRestricted()
