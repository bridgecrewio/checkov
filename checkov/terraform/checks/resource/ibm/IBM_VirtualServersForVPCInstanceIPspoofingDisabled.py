from __future__ import annotations

import itertools
from typing import Any

from checkov.common.util.type_forcers import force_list

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IBM_VirtualServersForVPCInstanceIPspoofingDisabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Virtual Machine scale sets Boot Diagnostics are Enabled"
        id = "CKV2_IBM_8"
        supported_resources = ("ibm_is_instance",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:

        primary_network_interfaces = force_list(conf.get('primary_network_interface', []))
        network_interfaces = force_list(conf.get('network_interfaces', []))

        allow_ip_spoofing_found = False

        # Check 'allow_ip_spoofing' in primary_network_interface
        for prim_nic_bloc in primary_network_interfaces:
            if prim_nic_bloc.get('allow_ip_spoofing', [False])[0]:
                allow_ip_spoofing_found = True

        # If 'allow_ip_spoofing' not found in primary_network_interface, check in network_interfaces
        if not allow_ip_spoofing_found:
            for nic_bloc in network_interfaces:
                if nic_bloc.get('allow_ip_spoofing', [False])[0]:
                    allow_ip_spoofing_found = True

        if allow_ip_spoofing_found:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = IBM_VirtualServersForVPCInstanceIPspoofingDisabled()
