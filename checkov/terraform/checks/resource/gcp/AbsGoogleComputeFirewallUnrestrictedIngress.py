from checkov.common.util.type_forcers import force_int

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AbsGoogleComputeFirewallUnrestrictedIngress(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources, port):
        super().__init__(name, id, categories, supported_resources)
        self.port = port

    def scan_resource_conf(self, conf):
        if 'allow' in conf:
            allow_blocks = conf['allow']
            for block in allow_blocks:
                if isinstance(block, str):
                    return CheckResult.UNKNOWN
                if 'ports' in block:
                    if self._is_port_in_range(block['ports']):
                        if 'source_ranges' in conf.keys():
                            source_ranges = conf['source_ranges'][0]
                            if "0.0.0.0/0" in source_ranges: # nosec
                                return CheckResult.FAILED
        return CheckResult.PASSED

    def _is_port_in_range(self, ports_list):
        for port_range in ports_list[0]:
            port = force_int(port_range)
            if port and self.port == port:
                return True
            if port is None and '-' in port_range:
                try:
                    [from_port, to_port] = port_range.split('-')
                    if int(from_port) <= self.port <= int(to_port):
                        return True
                except Exception:
                    return CheckResult.UNKNOWN
        return False
