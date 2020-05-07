from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class EKSSecretsEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EKS Cluster has Secrets Encryption Enabled"
        id = "CKV_AWS_58"
        supported_resources = ['aws_eks_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "encryption_config" in conf.keys() and "resources" in conf["encryption_config"][0] and \
                "secrets" in conf["encryption_config"][0]["resources"][0]:
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


check = EKSSecretsEncryption()
