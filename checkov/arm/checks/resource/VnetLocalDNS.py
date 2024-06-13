from ipaddress import ip_network, ip_address
from typing import Any, List, Dict

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class VnetLocalDNS(BaseResourceCheck):
    def __init__(self) -> None:
        """Avoid taking a dependency on external DNS servers
                 for local communication such as those deployed on-premises.
                Where possible consider deploying Azure Private DNS Zones,
                 a platform-as-a-service (PaaS) DNS service for VNETs"""

        name = "Ensure that VNET uses local DNS addresses"
        id = "CKV_AZURE_183"
        supported_resources = ("Microsoft.Network/virtualNetworks",)
        categories = [CheckCategories.NETWORKING, ]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Dict[str, Dict[str, List[Any]]]]) -> CheckResult:
        if "properties" in conf and "dhcpOptions" in conf["properties"]:
            if "dnsServers" in conf["properties"]["dhcpOptions"]:
                if isinstance(conf["properties"]["dhcpOptions"]["dnsServers"], list):
                    dns_servers = conf["properties"]["dhcpOptions"]["dnsServers"]
                    if dns_servers:
                        for ip in dns_servers:
                            if "addressSpace" in conf["properties"] and conf["properties"]["addressSpace"]:
                                if "addressPrefixes" in conf["properties"]["addressSpace"]:
                                    if isinstance(conf["properties"]["addressSpace"]["addressPrefixes"], list):
                                        address_spaces = conf["properties"]["addressSpace"]["addressPrefixes"]
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
                    self.evaluated_keys = ["dnsServers"]
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = VnetLocalDNS()
