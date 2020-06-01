from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
import re

DEFAULT_SERVICE_ACCOUNT = re.compile('\d+-compute@developer\.gserviceaccount\.com')
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
        if conf['name'][0].startswith('gke-'):
            return CheckResult.PASSED
        if 'service_account' in conf.keys():
            if 'email' in conf['service_account'][0]:
                if re.match(DEFAULT_SERVICE_ACCOUNT, conf['service_account'][0]['email'][0]):
                    if FULL_ACCESS_API in conf['service_account'][0]['scopes'][0]:
                        return CheckResult.FAILED
            elif FULL_ACCESS_API in conf['service_account'][0]['scopes'][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleComputeDefaultServiceAccountFullAccess()
