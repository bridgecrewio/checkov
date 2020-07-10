from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEBasicAuth(BaseResourceCheck):
    def __init__(self):
        name = "Ensure GKE basic auth is disabled"
        id = "CKV_GCP_19"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_compute_ssl_policy configuration
        :return: <CheckResult>
        """
        if 'master_auth' in conf.keys():
            if conf['master_auth'][0].get('username') or conf['master_auth'][0].get('password'):
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GKEBasicAuth()
