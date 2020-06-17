from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleComputeInstanceOSLogin(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that no instance in the project overrides the project setting for enabling OSLogin" \
               "(OSLogin needs to be enabled in prject metadata for all instances)"
        id = "CKV_GCP_34"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'metadata' in conf.keys():
            if 'enable-oslogin'in conf['metadata'][0]:
                if not conf['metadata'][0]['enable-oslogin']:
                    return CheckResult.FAILED
        return CheckResult.PASSED

    def get_inspected_key(self):
        return 'metadata/[0]/enable-oslogin'

    def get_bad_values(self):
        return [False]


check = GoogleComputeInstanceOSLogin()
