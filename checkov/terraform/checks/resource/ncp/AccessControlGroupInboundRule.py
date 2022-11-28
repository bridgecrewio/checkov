from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list


class AccessControlGroupInboundRule(BaseResourceCheck):
    def __init__(self, check_id: str, port: int) -> None:
        name = f"Ensure no access control groups allow inbound from 0.0.0.0:0 to port {port}"
        id = check_id
        supported_resource = ('ncloud_access_control_group_rule',)

        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)
        self.port = port

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:

        if 'inbound' in conf :  # This means it's an ACG resource with inbound block(s)
            inbound_conf = conf['inbound']
            for inbound_rule in inbound_conf:
                for rule in force_list(inbound_rule):
                    if isinstance(rule, dict) and self.contains_violation(rule):
                        self.evaluated_keys = [
                            f'inbound/[{inbound_conf.index(inbound_rule)}]/port_range',
                            f'inbound/[{inbound_conf.index(inbound_rule)}]/ip_block',
                        ]

                        return CheckResult.FAILED

        return CheckResult.PASSED

    def contains_violation(self, conf: dict[str, list[Any]]) -> bool:
        if 'port_range' in conf:
            port_range = conf.get('port_range')

            if isinstance(port_range, list):
                port_range = port_range[0].split("-")

                from_port = int(port_range[0])
                to_port = int(port_range[1]) if len(port_range) > 1 else from_port

                if to_port == 0 and from_port == 0:
                    to_port = 65535

                if from_port is not None and to_port is not None and (from_port <= self.port <= to_port):
                    conf_cidr_blocks = conf.get('ip_block', [[]])
                    if conf_cidr_blocks:
                        conf_cidr_blocks = conf_cidr_blocks[0]
                    cidr_blocks = force_list(conf_cidr_blocks)

                    if '0.0.0.0/0' in cidr_blocks:
                        return True

        return False
