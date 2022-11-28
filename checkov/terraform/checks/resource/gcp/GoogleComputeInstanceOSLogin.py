from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class GoogleComputeInstanceOSLogin(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that no instance in the project overrides the project setting for enabling OSLogin" \
               "(OSLogin needs to be enabled in project metadata for all instances)"
        id = "CKV_GCP_34"
        supported_resources = ['google_compute_instance', 'google_compute_instance_template',
                               'google_compute_instance_from_template']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if ('source_instance_template' in conf.keys() and 'metadata' not in conf.keys()) or \
                ('source_instance_template' in conf.keys() and isinstance(conf['metadata'][0], dict) and 'enable-oslogin' not in
                 conf['metadata'][0].keys()):
            # if the source_instance_template value is there (indicating a google_compute_instance_from_template),
            # and enable-oslogin is not present, then this check cannot PASS, since we don't know what the
            # underlying source template looks like.
            return CheckResult.UNKNOWN
        else:
            # in all other cases, pass/fail the check if block-project-ssh-keys is true/false or not present.
            return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'metadata/[0]/enable-oslogin'

    def get_forbidden_values(self):
        return [False]


check = GoogleComputeInstanceOSLogin()
