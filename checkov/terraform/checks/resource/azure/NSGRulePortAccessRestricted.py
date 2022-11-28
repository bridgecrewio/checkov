from typing import Union, List, Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
import re

INTERNET_ADDRESSES = ("*", "0.0.0.0", "<nw>/0", "/0", "internet", "any")  # nosec
PORT_RANGE = re.compile(r"\d+-\d+")


class NSGRulePortAccessRestricted(BaseResourceCheck):
    def __init__(self, name: str, check_id: str, port: int) -> None:
        supported_resources = ("azurerm_network_security_rule", "azurerm_network_security_group")
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)
        self.port = port

    def is_port_in_range(self, ports: Union[int, str, List[Union[int, str]]]) -> bool:
        for range in force_list(ports):
            str_range = str(range)
            if re.match(PORT_RANGE, str_range):
                start, end = int(range.split("-")[0]), int(range.split("-")[1])
                if start <= self.port <= end:
                    return True
            if str_range in (str(self.port), "*"):
                return True
        return False

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        rule_confs = [conf]
        evaluated_key_prefix = ""
        if "security_rule" in conf:
            rule_confs = conf["security_rule"]
            self.evaluated_keys = ["security_rule"]
            evaluated_key_prefix = "security_rule/"

        for rule_conf in rule_confs:
            if not isinstance(rule_conf, dict):
                return CheckResult.UNKNOWN

            access = rule_conf.get("access")
            direction = rule_conf.get("direction")
            protocol = rule_conf.get("protocol")
            destination_port_range = rule_conf.get("destination_port_range")
            destination_port_ranges = rule_conf.get("destination_port_ranges")
            source_address_prefix = rule_conf.get("source_address_prefix")
            source_address_prefixes = rule_conf.get("source_address_prefixes")

            if (
                access
                and access[0].lower() == "allow"
                and direction
                and direction[0].lower() == "inbound"
                and protocol
                and protocol[0].lower() in ("tcp", "*")
                and (
                    (
                        destination_port_range
                        and self.is_port_in_range(destination_port_range[0])  # fmt: skip
                    )
                    or (
                        destination_port_ranges
                        and destination_port_ranges[0]
                        and any(self.is_port_in_range(range) for range in destination_port_ranges[0])
                    )
                )
                and (
                    (
                        source_address_prefix
                        and isinstance(source_address_prefix[0], str)
                        and source_address_prefix[0].lower() in INTERNET_ADDRESSES  # fmt: skip
                    )
                    or (
                        source_address_prefixes
                        and source_address_prefixes[0]
                        and isinstance(source_address_prefixes[0], list)
                        and any((isinstance(prefix, str) and prefix.lower()) in INTERNET_ADDRESSES for prefix in
                                source_address_prefixes[0])
                    )
                )
            ):
                evaluated_key_prefix = (
                    f"{evaluated_key_prefix}[{rule_confs.index(rule_conf)}]/" if evaluated_key_prefix else ""
                )
                self.evaluated_keys = [
                    f"{evaluated_key_prefix}access",
                    f"{evaluated_key_prefix}direction",
                    f"{evaluated_key_prefix}protocol",
                    f"{evaluated_key_prefix}destination_port_range",
                    f"{evaluated_key_prefix}destination_port_ranges",
                    f"{evaluated_key_prefix}source_address_prefix",
                    f"{evaluated_key_prefix}source_address_prefixes",
                ]
                return CheckResult.FAILED

        return CheckResult.PASSED
