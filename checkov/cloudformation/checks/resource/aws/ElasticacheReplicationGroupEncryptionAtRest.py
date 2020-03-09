from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ElasticacheReplicationGroupEncryptionAtRest(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticache Replication Group  is securely encrypted at rest"
        id = "CKV_AWS_29"
        supported_resources = ['AWS::ElastiCache::ReplicationGroup']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_elasticache_replication_group:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html
        :param conf: aws_elasticache_replication_group configuration
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'AtRestEncryptionEnabled' in conf['Properties'].keys():
                if conf['Properties']['AtRestEncryptionEnabled'] == True:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = ElasticacheReplicationGroupEncryptionAtRest()
