from checkov.common.util.type_forcers import force_int

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AbsGoogleComputeFirewallUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources, port):
        super().__init__(name, id, categories, supported_resources)
        self.port = port

    def scan_resource_conf(self, conf):
        if self._is_disabled(conf):
            self.evaluated_keys = ['disabled']
            return CheckResult.PASSED
        if 'allow' in conf:
            allow_blocks = conf['allow']
            self.evaluated_keys = ['allow']
            for block in allow_blocks:
                if isinstance(block, str):
                    self.evaluated_keys = [f'allow/[{allow_blocks.index(block)}]']
                    return CheckResult.UNKNOWN
                # An allow block with no ports list permits every port of that protocol.
                if 'ports' not in block and self._protocol(block) in {'tcp', 'all'}:
                    if self._open_to_internet(conf):
                        self.evaluated_keys = [f'allow/[{allow_blocks.index(block)}]/protocol', 'source_ranges']
                        return CheckResult.FAILED
                if 'ports' in block:
                    if self._is_port_in_range(block['ports']):
                        if self._open_to_internet(conf):
                            self.evaluated_keys = [f'allow/[{allow_blocks.index(block)}]/ports', 'source_ranges']
                            return CheckResult.FAILED
        return CheckResult.PASSED

    def _is_disabled(self, conf):
        values = conf.get('disabled') or []
        if not values:
            return False
        value = values[0]
        if isinstance(value, list):
            value = value[0] if value else False
        if isinstance(value, str):
            return value.lower() == 'true'
        return value is True

    def _protocol(self, block):
        protocol = block.get('protocol')
        if isinstance(protocol, list):
            protocol = protocol[0] if protocol else ''
        if not isinstance(protocol, str):
            return ''
        return protocol.lower()

    def _open_to_internet(self, conf):
        source_ranges_list = conf.get('source_ranges', [])
        if not source_ranges_list:
            return False
        source_ranges = source_ranges_list[0]
        return bool(source_ranges) and "0.0.0.0/0" in source_ranges  # nosec

    def _is_port_in_range(self, ports_list):
        if len(ports_list) == 0:
            return False
        if isinstance(ports_list[0], list):
            ports_list = ports_list[0]
        for port_range in ports_list:
            port = force_int(port_range)
            if port and self.port == port:
                return True
            if port is None and port_range and '-' in port_range:
                try:
                    [from_port, to_port] = port_range.split('-')
                    if int(from_port) <= self.port <= int(to_port):
                        return True
                except Exception:
                    return CheckResult.UNKNOWN
        return False
