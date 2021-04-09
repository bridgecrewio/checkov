from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class KubernetesSecretsEncryptedUsingCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Kubernetes Secrets are encrypted using Customer Master Keys (CMKs) managed in AWS KMS"
        id = "CKV_AWS_106"
        supported_resources = ['aws_eks_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'encryption_config' not in conf.keys():
            return CheckResult.FAILED
        else:
            encryption_config = conf.get('encryption_config')[0]
            if 'resources' in encryption_config and 'provider' in encryption_config:
                resources = encryption_config.get('resources')[0]
                provider = encryption_config.get('provider')[0]
                if type(resources) is list:
                    if 'secrets' in resources and 'key_arn' in provider:
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = KubernetesSecretsEncryptedUsingCMK()
