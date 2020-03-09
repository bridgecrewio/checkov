from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class GoogleContainerClusterClientCertificateEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure a client certificate is used by clients to authenticate to Kubernetes Engine Clusters"
        id = "CKV_GCP_13"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for client certificate configuration on google_container_cluster:
            https://www.terraform.io/docs/providers/google/r/container_cluster.html#client_certificate_config
        :param conf: google_container_cluster configuration
        :return: <CheckResult>
        """
        if 'master_auth' in conf and 'client_certificate_config' in conf['master_auth'][0]:
            if 'issue_client_certificate' in conf['master_auth'][0]['client_certificate_config'][0]:
                if conf['master_auth'][0]['client_certificate_config'][0]['issue_client_certificate'][0]:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleContainerClusterClientCertificateEnabled()
