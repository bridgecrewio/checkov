from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import re

INTERNET_ADDRESSES = ["*", "0.0.0.0", "<nw>/0", "/0", "internet", "any"] # nosec
PORT_RANGE = re.compile('\d+-\d+')


class NSGRulePortAccessRestricted(BaseResourceCheck):
    def __init__(self, name, check_id, port):
        supported_resources = ['azurerm_network_security_rule', 'azurerm_network_security_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def is_port_in_range(self, conf):
        ports = force_list(conf['destination_port_range'][0])
        for range in ports:
            str_range = str(range)
            if re.match(PORT_RANGE, str_range):
                start, end = int(range.split('-')[0]), int(range.split('-')[1])
                if start <= self.port <= end:
                    return True
            if str_range in [str(self.port), '*']:
                return True
        return False

    def scan_resource_conf(self, conf):
        if "dynamic" in conf:
            return CheckResult.UNKNOWN

        rule_confs = [conf]
        if 'security_rule' in conf:
            rule_confs = conf['security_rule']

        for rule_conf in rule_confs:
            if not isinstance(rule_conf, dict):
                return CheckResult.UNKNOWN
            if 'access' in rule_conf and rule_conf['access'][0].lower() == "allow":
                if 'direction' in rule_conf and rule_conf['direction'][0].lower() == "inbound":
                    if 'protocol' in rule_conf and rule_conf['protocol'][0].lower() in ['tcp', '*']:
                        if 'destination_port_range' in rule_conf and self.is_port_in_range(rule_conf):
                            if 'source_address_prefix' in rule_conf and rule_conf['source_address_prefix'][0].lower() in INTERNET_ADDRESSES:
                                return CheckResult.FAILED
        return CheckResult.PASSED

