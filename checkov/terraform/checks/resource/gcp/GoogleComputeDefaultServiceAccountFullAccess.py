from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
import re

DEFAULT_SERVICE_ACCOUNT = re.compile(r'\d+-compute@developer\.gserviceaccount\.com')
FULL_ACCESS_API = 'https://www.googleapis.com/auth/cloud-platform'


class GoogleComputeDefaultServiceAccountFullAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that instances are not configured to use the default service account with full access" \
               " to all Cloud APIs"
        id = "CKV_GCP_31"
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
        if 'name' in conf and conf['name'][0].startswith('gke-'):
            self.evaluated_keys = ['name']
            return CheckResult.PASSED
        if 'service_account' in conf.keys():
            service_account_conf = conf['service_account'][0]
            self.evaluated_keys = ['service_account']
            if isinstance(service_account_conf, dict):
                self.evaluated_keys = ['service_account/[0]/scopes']
                if 'email' in service_account_conf:
                    self.evaluated_keys.append('service_account/[0]/email')
                    if re.match(DEFAULT_SERVICE_ACCOUNT, service_account_conf['email'][0]):
                        if len(service_account_conf['scopes']) > 0 and FULL_ACCESS_API in service_account_conf['scopes'][0]:
                            return CheckResult.FAILED
                elif len(service_account_conf['scopes']) > 0 and FULL_ACCESS_API in service_account_conf['scopes'][0]:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleComputeDefaultServiceAccountFullAccess()
