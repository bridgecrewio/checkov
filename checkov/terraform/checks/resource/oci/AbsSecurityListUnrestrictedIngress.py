from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AbsSecurityListUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, check_id, port, is_exposed_by_default):
        name = f"Ensure no security list allow ingress from 0.0.0.0:0 to port {port}."
        supported_resources = ['oci_core_security_list']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port
        self.is_exposed_by_default = is_exposed_by_default

    def scan_resource_conf(self, conf):
        if 'ingress_security_rules' in conf:
            self.evaluated_keys = ['ingress_security_rules']
            rules = conf.get("ingress_security_rules", [])

            for idx, rule in enumerate(rules):
                if "0.0.0.0/0" in rule['source'][0] \
                        and (
                        (rule['protocol'][0] != '1' and ('udp_options' not in rule) and ('tcp_options' not in rule))
                        or self.scan_protocol_conf(rule, 'tcp_options', idx) != CheckResult.FAILED
                        or self.scan_protocol_conf(rule, 'udp_options', idx) != CheckResult.FAILED
                        or rule['protocol'][0] == 'all'):
                    self.evaluated_keys = [f'ingress_security_rules/[0]/[{idx}]']
                    return CheckResult.FAILED

            return CheckResult.PASSED

        return CheckResult.FAILED if self.is_exposed_by_default else CheckResult.PASSED

    def scan_protocol_conf(self, rule, protocol_name, idx):
        """ scan udp/tcp_options configuration"""
        if protocol_name in rule:
            max_port = rule[protocol_name][0]['max'][0]
            min_port = rule[protocol_name][0]['min'][0]
            if min_port <= self.port and max_port >= self.port:
                return CheckResult.SKIPPED
        self.evaluated_keys = [f'ingress_security_rules/[0]/[{idx}]/protocol/[0]/{protocol_name}']
        return CheckResult.FAILED
