from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GKEUseCosImage(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Container-Optimized OS (cos) is used for Kubernetes Engine Clusters Node image"
        id = "CKV_GCP_22"
        supported_resources = ['google_container_node_pool']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_compute_ssl_policy configuration
        :return: <CheckResult>
        """
        if 'node_config' in conf:
            node_config = conf.get('node_config', [{}])[0]
            self.evaluated_keys = ['node_config']
            if not isinstance(node_config, dict):
                return CheckResult.UNKNOWN

            if conf.get('node_config', [{}])[0].get('image_type', [''])[0].lower().startswith('cos'):
                self.evaluated_keys = ['node_config/[0]/image_type']
                return CheckResult.PASSED
            if conf.get('remove_default_node_pool', [{}])[0]:
                self.evaluated_keys.append('remove_default_node_pool')
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GKEUseCosImage()
