from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class GoogleComputeSerialPorts(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure 'Enable connecting to serial ports' is not enabled for VM Instance"
        id = "CKV_GCP_35"
        supported_resources = ['google_compute_instance', 'google_compute_instance_template',
                               'google_compute_instance_from_template']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if ('source_instance_template' in conf.keys() and 'metadata' not in conf.keys()) or \
                ('source_instance_template' in conf.keys() and isinstance(conf['metadata'][0], dict) and 'serial-port-enable' not in
                 conf['metadata'][0].keys()):
            # if the source_instance_template value is there (indicating a google_compute_instance_from_template),
            # and serial-port-enable is not present, then this check cannot PASS, since we don't know what the
            # underlying source template looks like.
            return CheckResult.UNKNOWN
        else:
            # in all other cases, pass/fail the check if block-project-ssh-keys is true/false or not present.
            return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'metadata/[0]/serial-port-enable'

    def get_forbidden_values(self):
        return [True]


check = GoogleComputeSerialPorts()
