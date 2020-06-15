from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class NeptuneClusterStorageEncrypted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Neptune storage is securely encrypted"
        id = "CKV_AWS_44"
        supported_resources = ['AWS::Neptune::DBCluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for encryption configuration of a Neptune DB cluster
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-neptune-dbcluster.html#cfn-neptune-dbcluster-storageencrypted
        :param conf: aws_neptune_db_cluster
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if conf['Properties'].get('StorageEncrypted'):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = NeptuneClusterStorageEncrypted()
