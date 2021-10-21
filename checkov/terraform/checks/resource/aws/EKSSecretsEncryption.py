from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class EKSSecretsEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EKS Cluster has Secrets Encryption Enabled"
        id = "CKV_AWS_58"
        supported_resources = ['aws_eks_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # AWS EKS provider uses "encryption_config"
        # AWS EKS module uses "cluster_encryption_config"
        encryption_config = conf.get('encryption_config') or conf.get(
            'cluster_encryption_config')
        if encryption_config is None:
            return CheckResult.FAILED
        self.evaluated_keys = ["encryption_config"]
        if not isinstance(encryption_config, list):
            return CheckResult.FAILED
        node = encryption_config[0]
        self.evaluated_keys = ["encryption_config/[0]"]
        if not isinstance(node, dict):
            return CheckResult.FAILED
        resources = node.get('resources')
        if isinstance(resources, list) and len(resources) == 1:
            resources = resources[0]
        if resources == ["secrets"]:
            self.evaluated_keys = ["encryption_config/[0]/resources"]
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


check = EKSSecretsEncryption()
