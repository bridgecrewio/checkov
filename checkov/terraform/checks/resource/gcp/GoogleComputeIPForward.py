from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class GoogleComputeIPForward(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that IP forwarding is not enabled on Instances"
        id = "CKV_GCP_36"
        supported_resources = ['google_compute_instance', 'google_compute_instance_template',
                               'google_compute_instance_from_template']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if 'source_instance_template' in conf.keys() and 'can_ip_forward' not in conf.keys():
            # if the source_instance_template value is there (indicating a google_compute_instance_from_template),
            # and can_ip_forward is not present, then this check cannot PASS, since we don't know what the
            # underlying source template looks like.
            return CheckResult.UNKNOWN
        else:
            # in all other cases, pass/fail the check if block-project-ssh-keys is true/false or not present.
            return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'can_ip_forward'

    def get_forbidden_values(self):
        return [True]

    def get_excluded_key(self):
        return "name"

    def check_excluded_condition(self, value):
        return value.startswith('gke-')


check = GoogleComputeIPForward()
