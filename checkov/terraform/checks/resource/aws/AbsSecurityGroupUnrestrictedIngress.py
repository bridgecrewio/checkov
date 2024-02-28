from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
from checkov.common.util.type_forcers import force_int


class AbsSecurityGroupUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, check_id: str, port: int) -> None:
        name = f"Ensure no security groups allow ingress from 0.0.0.0:0 to port {port}"
        supported_resources = ('aws_security_group', 'aws_security_group_rule', 'aws_vpc_security_group_ingress_rule')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        """
            Looks for configuration at security group ingress rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
            https://www.terraform.io/docs/providers/aws/r/security_group_rule.html

            Return PASS if:
            - The resource is an aws_security_group that contains no violating ingress rules (including if there are no
              ingress rules at all), OR
            - The resource is an aws_security_group_rule of type 'ingress' that does not violate the check.

            Return FAIL if:
            - The resource is an aws_security_group that contains a violating ingress rule, OR
            - The resource is an aws_security_group_rule of type 'ingress' that violates the check.

            Return UNKNOWN if:
            - the resource is an aws_security_group_rule of type 'egress', OR

        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """

        if 'ingress' in conf:  # This means it's an SG resource with ingress block(s)
            ingress_conf = conf['ingress']
            for ingress_rule in ingress_conf:
                for rule in force_list(ingress_rule):
                    if isinstance(rule, dict):
                        if self.check_self(rule):
                            return CheckResult.PASSED
                        if self.contains_violation(rule):
                            self.evaluated_keys = [
                                f'ingress/[{ingress_conf.index(ingress_rule)}]/from_port',
                                f'ingress/[{ingress_conf.index(ingress_rule)}]/to_port',
                                f'ingress/[{ingress_conf.index(ingress_rule)}]/cidr_blocks',
                                f'ingress/[{ingress_conf.index(ingress_rule)}]/ipv6_cidr_blocks',
                            ]
                            return CheckResult.FAILED

            return CheckResult.PASSED

        if 'type' in conf:  # This means it's an SG_rule resource.
            type = force_list(conf['type'])[0]
            if type == 'ingress':
                if self.check_self(conf):
                    return CheckResult.PASSED
                self.evaluated_keys = ['from_port', 'to_port', 'cidr_blocks', 'ipv6_cidr_blocks']
                if self.contains_violation(conf):
                    return CheckResult.FAILED
                return CheckResult.PASSED
            return CheckResult.UNKNOWN
        else:
            self.evaluated_keys = ['from_port', 'to_port', 'cidr_ipv4', 'cidr_ipv6']
            if 'from_port' in conf or 'to_port' in conf:
                if self.contains_violation(conf):
                    return CheckResult.FAILED
                return CheckResult.PASSED

        return CheckResult.PASSED

    def contains_violation(self, conf: dict[str, list[Any]]) -> bool:
        from_port = force_int(force_list(conf.get('from_port', [{-1}]))[0])
        to_port = force_int(force_list(conf.get('to_port', [{-1}]))[0])
        protocol = force_list(conf.get('protocol', [None]))[0]
        if from_port == 0 and to_port == 0:
            to_port = 65535

        prefix_list_ids = conf.get('prefix_list_ids')
        if prefix_list_ids and prefix_list_ids != [[]]:
            return False

        if from_port is not None and to_port is not None and (from_port <= self.port <= to_port) or (
                protocol == '-1' and from_port == 0 and to_port == 65535):
            if conf.get('cidr_blocks'):
                conf_cidr_blocks = conf.get('cidr_blocks', [[]])
            else:
                conf_cidr_blocks = conf.get('cidr_ipv4', [[]])
            if conf_cidr_blocks and len(conf_cidr_blocks) > 0:
                conf_cidr_blocks = conf_cidr_blocks[0]
            cidr_blocks = force_list(conf_cidr_blocks)
            if "0.0.0.0/0" in cidr_blocks:
                return True
            if conf.get('ipv6_cidr_blocks'):
                ipv6_cidr_blocks = conf.get('ipv6_cidr_blocks', [])
            else:
                ipv6_cidr_blocks = conf.get('cidr_ipv6', [])
            if ipv6_cidr_blocks and ipv6_cidr_blocks[0] is not None and \
                    any(ip in ['::/0', '0000:0000:0000:0000:0000:0000:0000:0000/0'] for ip in ipv6_cidr_blocks[0]):
                return True
            if not ipv6_cidr_blocks and not cidr_blocks \
                    and conf.get('security_groups') is None \
                    and conf.get('source_security_group_id') is None:
                return True
        return False

    def check_self(self, conf: dict[str, list[Any]]) -> bool:
        if conf.get('self'):
            limit = force_list(conf['self'])[0]
            if limit:
                return True
        return False
