from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
from checkov.common.util.type_forcers import force_int


class AbsSecurityGroupUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, check_id, port):
        name = "Ensure no security groups allow ingress from 0.0.0.0:0 to port %d" % port
        supported_resources = ['alicloud_security_group_rule']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def scan_resource_conf(self, conf):
        """
            Looks for configuration at security group ingress rules :
            https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/security_group_rule

            Return PASS if:
            - The resource is an alicloud_security_group_rule of type 'ingress' that does not violate the check.

            Return FAIL if:
            - The resource is an alicloud_security_group_rule of type 'ingress' that violates the check.

            Return UNKNOWN if:
            - the resource is an alicloud_security_group_rule of type 'egress'

        :param conf: alicloud_security_group_rule configuration
        :return: <CheckResult>
        """

        if 'type' not in conf:  # This means it's not an alicloud_security_group_rule resource.
            return CheckResult.PASSED

        rule_type = force_list(conf['type'])[0]
        if rule_type != 'ingress':
            return CheckResult.UNKNOWN
        self.evaluated_keys = ['port_range', 'cidr_ip']
        if not conf.get('port_range'):
            return CheckResult.PASSED
        if self.contains_violation(conf):
            return CheckResult.FAILED
        return CheckResult.PASSED

    def contains_violation(self, conf):
        try:
            from_port = force_int(force_list(conf.get('port_range', [{-1}]))[0].split('/')[0])
            to_port = force_int(force_list(conf.get('port_range', [{-1}]))[0].split('/')[1])
        except Exception:
            return False

        if from_port and to_port and from_port <= self.port <= to_port:
            conf_cidr_blocks = conf.get('cidr_ip', [[]])
            cidr_blocks = force_list(conf_cidr_blocks)
            if "0.0.0.0/0" in cidr_blocks or not cidr_blocks[0]:
                return True
        return False
