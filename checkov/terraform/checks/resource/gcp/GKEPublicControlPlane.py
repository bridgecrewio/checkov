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
            Looks for master authorized networks configuration at google_container_cluster:
            https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster#master_authorized_networks_config
        :param conf: google_container_cluster configuration
        :return: <CheckResult>
        """
        if self._has_private_endpoint(conf):
            # no public endpoint exists, so the control plane cannot be public
            return CheckResult.PASSED
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
            return CheckResult.PASSED
        # Master Authorized Networks are disabled by default, so without this
        # block the control plane public endpoint accepts traffic from any IP
        return CheckResult.FAILED

    @staticmethod
    def _has_private_endpoint(conf):
        private_cluster_conf = conf.get('private_cluster_config')
        if (isinstance(private_cluster_conf, list) and len(private_cluster_conf) > 0
                and isinstance(private_cluster_conf[0], dict)
                and 'enable_private_endpoint' in private_cluster_conf[0]):
            value = private_cluster_conf[0]['enable_private_endpoint']
            return isinstance(value, list) and len(value) > 0 and value[0] is True
        return False


check = GKEPublicControlPlane()
