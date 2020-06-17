from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleComputeSerialPorts(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure 'Enable connecting to serial ports' is not enabled for VM Instance"
        id = "CKV_GCP_35"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'metadata' in conf.keys():
            if 'serial-port-enable' in conf['metadata'][0]:
                if conf['metadata'][0]['serial-port-enable'] not in ['0', False]:
                    return CheckResult.FAILED
        return CheckResult.PASSED

    def get_inspected_key(self):
        return 'metadata/[0]/serial-port-enable'

    def get_bad_values(self):
        return ['1', True]


check = GoogleComputeSerialPorts()
