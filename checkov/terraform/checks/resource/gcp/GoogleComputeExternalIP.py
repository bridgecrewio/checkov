from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class GoogleComputeExternalIP(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that Compute instances do not have public IP addresses"
        id = "CKV_GCP_40"
        supported_resources = ['google_compute_instance', 'google_compute_instance_template',
                               'google_compute_instance_from_template']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if 'source_instance_template' in conf.keys() and 'network_interface' not in conf.keys():
            # if the source_instance_template value is there (indicating a google_compute_instance_from_template),
            # and the networks _interface block is not present, then this check cannot PASS,
            # since we don't know what the underlying source template looks like.
            return CheckResult.UNKNOWN
        else:
            # in all other cases, pass/fail the check if block-project-ssh-keys is true/false or not present.
            return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'network_interface/[0]/access_config'

    def get_forbidden_values(self):
        return [ANY_VALUE]


check = GoogleComputeExternalIP()
