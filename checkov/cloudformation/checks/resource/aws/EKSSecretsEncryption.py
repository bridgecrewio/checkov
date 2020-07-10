from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class EKSSecretsEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EKS Cluster has Secrets Encryption Enabled"
        id = "CKV_AWS_58"
        supported_resources = ['AWS::EKS::Cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for eks secrets encryption
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-cluster-encryptionconfig.html
        :param conf: AWS::EKS::Cluster configuration
        :return: <CheckResult>
        """
        if 'EncryptionConfig' in conf['Properties'].keys() and 'Resources' in conf['Properties']['EncryptionConfig'][0] \
                and 'secrets' in conf['Properties']['EncryptionConfig'][0]['Resources']:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = EKSSecretsEncryption()
