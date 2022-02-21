from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEPublicControlPlane(BaseResourceCheck):
    def __init__(self):
        name = "Ensure GKE Control Plane is not public"
        id = "CKV_GCP_18"
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
        if 'master_authorized_networks_config' in conf.keys():
            self.evaluated_keys = ['master_authorized_networks_config']
            master_authorized_networks_conf = conf['master_authorized_networks_config'][0]
            if isinstance(master_authorized_networks_conf, dict) and 'cidr_blocks' in master_authorized_networks_conf:
                cidr_blocks_conf = master_authorized_networks_conf['cidr_blocks']
                for cidr_block_conf in cidr_blocks_conf:
                    if isinstance(cidr_block_conf, dict) and '0.0.0.0/0' in cidr_block_conf['cidr_block']:  # nosec
                        self.evaluated_keys = [f'master_authorized_networks_config/[0]/cidr_blocks/'
                                               f'[{cidr_blocks_conf.index(cidr_block_conf)}]/cidr_block']
                        return CheckResult.FAILED
                self.evaluated_keys = ['master_authorized_networks_config/[0]/cidr_blocks']
        return CheckResult.PASSED


check = GKEPublicControlPlane()
