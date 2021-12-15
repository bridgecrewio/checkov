from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleComputeBlockProjectSSH(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure 'Block Project-wide SSH keys' is enabled for VM instances"
        id = "CKV_GCP_32"
        supported_resources = ['google_compute_instance', 'google_compute_instance_template',
                               'google_compute_instance_from_template']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if ('source_instance_template' in conf.keys() and 'metadata' not in conf.keys()) or \
                ('source_instance_template' in conf.keys() and 'block-project-ssh-keys' not in
                 conf['metadata'][0].keys()):
            # if the source_instance_template value is there (indicating a google_compute_instance_from_template),
            # and block-project-ssh-keys is not present, then this check cannot PASS, since we don't know what the
            # underlying source template looks like.
            return CheckResult.UNKNOWN
        else:
            # in all other cases, pass/fail the check if block-project-ssh-keys is true/false or not present.
            return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'metadata/block-project-ssh-keys'


check = GoogleComputeBlockProjectSSH()
