from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
from checkov.common.util.type_forcers import force_int


class AbsSecurityGroupUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, check_id, port):
        name = f"Ensure no security groups allow ingress from 0.0.0.0:0 to port {port:d} (tcp / udp)"
        supported_resources = ['openstack_compute_secgroup_v2', 'openstack_networking_secgroup_rule_v2']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def scan_resource_conf(self, conf):
        """
            Looks for configuration at security group ingress rules:
            https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/compute_secgroup_v2
            https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/networking_secgroup_rule_v2

            Return PASS if:
            - the resource is an openstack_compute_secgroup_v2 that contains no violating rules (including if there are
              no rules at all), OR
            - the resource is an openstack_networking_secgroup_rule_v2 of type 'ingress' that does not violate the
              check.

            Return FAIL if:
            - the resource is an openstack_compute_secgroup_v2 that contains a violating rule, OR
            - the resource is an openstack_networking_secgroup_rule_v2 of type 'ingress' that violates the check.

            Return UNKNOWN if:
            - the resource is an openstack_networking_secgroup_rule_v2 of type 'egress'

        :param conf: openstack_compute_secgroup_v2|openstack_networking_secgroup_rule_v2 configuration
        :return: <CheckResult>
        """

        if 'rule' in conf:  # This means it's an SG resource with rule block(s)
            rules = conf['rule']
            for rule in rules:
                if isinstance(rule, dict) and self.contains_violation(rule, 'ip_protocol', 'from_port', 'to_port',
                                                                      'cidr'):
                    self.evaluated_keys = [
                        f'rule/[{rules.index(rule)}]/ip_protocol',
                        f'rule/[{rules.index(rule)}]/from_port',
                        f'rule/[{rules.index(rule)}]/to_port',
                        f'rule/[{rules.index(rule)}]/cidr',
                    ]
                    return CheckResult.FAILED

            return CheckResult.PASSED

        if 'direction' in conf:  # This means it's an SG_rule resource.
            direction = force_list(conf['direction'])[0]
            if direction == 'ingress':
                self.evaluated_keys = ['protocol', 'port_range_min', 'port_range_max', 'remote_ip_prefix']
                if self.contains_violation(conf, 'protocol', 'port_range_min', 'port_range_max', 'remote_ip_prefix'):
                    return CheckResult.FAILED
                return CheckResult.PASSED
            return CheckResult.UNKNOWN

        # The result for an SG with no ingress block
        return CheckResult.PASSED

    def contains_violation(self, conf, protocol_key, from_port_key, to_port_key, cidr_key):
        protocol = force_list(conf.get(protocol_key, [{-1}]))[0]
        from_port = force_int(force_list(conf.get(from_port_key, [{-1}]))[0])
        to_port = force_int(force_list(conf.get(to_port_key, [{-1}]))[0])

        if protocol == "icmp":
            return False

        if from_port is not None and to_port is not None and (from_port <= self.port <= to_port):
            cidr = conf.get(cidr_key, [])
            if len(cidr) > 0 and cidr[0] in ['0.0.0.0/0', '::/0', '0000:0000:0000:0000:0000:0000:0000:0000/0']:
                return True
        return False
