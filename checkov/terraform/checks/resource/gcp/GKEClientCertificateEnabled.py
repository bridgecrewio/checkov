from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GKEClientCertificateEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure a client certificate is used by clients to authenticate to Kubernetes Engine Clusters"
        id = "CKV_GCP_13"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
                    Looks for client certificate configuration on google_container_cluster:
                    https://www.terraform.io/docs/providers/google/r/container_cluster.html#client_certificate_config
                :param conf: google_container_cluster configuration
                :return: <CheckResult>
        """
        return 'master_auth/[0]/client_certificate_config/[0]/issue_client_certificate/[0]'


check = GKEClientCertificateEnabled()
