
from checkov.common.models.enums import CheckCategories,CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import Dict, List, Any
from checkov.common.util.type_forcers import force_list


class FirewallIngressOpen(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the firewall ingress is not wide open"
        id = "CKV_DIO_4"
        supported_resources = ['digitalocean_firewall']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'inbound_rule' in conf.keys():
            ingress_conf = conf['inbound_rule']
            for ingress_rule in ingress_conf:
                ingress_rules = force_list(ingress_rule)
                for rule in ingress_rules:
                    if rule['source_addresses']:
                        sources = rule["source_addresses"][0]
                        if any(item in ["0.0.0.0/0", "::/0"] for item in sources):
                           self.evaluated_keys=["inbound_rule/[0]/source_addresses"]
                           return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.PASSED


check = FirewallIngressOpen()
