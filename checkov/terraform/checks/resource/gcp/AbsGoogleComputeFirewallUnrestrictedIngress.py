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
                if 'ports' in block.keys():
                    if self.port in block['ports'][0]:
                        if 'source_ranges' in conf.keys():
                            source_ranges = conf['source_ranges'][0]
                            if "0.0.0.0/0" in source_ranges:
                                return CheckResult.FAILED
        return CheckResult.PASSED
