from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
import re

DEFAULT_SERVICE_ACCOUNT = re.compile(r'\d+-compute@developer\.gserviceaccount\.com')


class GoogleComputeDefaultServiceAccount(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that instances are not configured to use the default service account"
        id = "CKV_GCP_30"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for service account configuration at google_compute_instance:
            https://www.terraform.io/docs/providers/google/r/compute_instance.html
        :param conf: google_compute_instance configuration
        :return: <CheckResult>
        """
        if 'service_account' in conf.keys():
            if 'email' in conf['service_account'][0]:
                if not re.match(DEFAULT_SERVICE_ACCOUNT, conf['service_account'][0]['email'][0]):
                    return CheckResult.PASSED
        if 'name' in conf and conf['name'][0].startswith('gke-'):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleComputeDefaultServiceAccount()
