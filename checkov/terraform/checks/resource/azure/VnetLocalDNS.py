from __future__ import annotations

from ipaddress import ip_network, ip_address
from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class VnetLocalDNS(BaseResourceCheck):
    def __init__(self) -> None:
        """Avoid taking a dependency on external DNS servers
         for local communication such as those deployed on-premises.
        Where possible consider deploying Azure Private DNS Zones,
         a platform-as-a-service (PaaS) DNS service for VNETs"""
        name = "Ensure that VNET uses local DNS addresses"
        id = "CKV_AZURE_183"
        supported_resources = ("azurerm_virtual_network",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "dns_servers" in conf and conf["dns_servers"] and isinstance(conf["dns_servers"], list):
            dns_servers = conf["dns_servers"][0]
            if dns_servers:
                for ip in dns_servers:
                    if "address_space" in conf and conf["address_space"] and isinstance(conf["address_space"], list):
                        address_spaces = conf["address_space"][0]
                        if isinstance(address_spaces, list):
                            for address_range in address_spaces:
                                if not isinstance(address_range, str):
                                    continue
                                try:
                                    net = ip_network(address_range)
                                    ip_add = ip_address(ip) if isinstance(ip, str) else None
                                except ValueError:
                                    return CheckResult.UNKNOWN
                                if isinstance(ip, str) and ip_add in net:
                                    return CheckResult.PASSED
                self.evaluated_keys = ["dns_servers"]
                return CheckResult.FAILED
        return CheckResult.PASSED


check = VnetLocalDNS()
