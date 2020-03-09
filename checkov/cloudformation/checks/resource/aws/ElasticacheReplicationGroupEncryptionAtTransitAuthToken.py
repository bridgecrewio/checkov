from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ElasticacheReplicationGroupEncryptionAtTransitAuthToken(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticache Replication Group is securely encrypted at transit and has auth token"
        id = "CKV_AWS_31"
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
            if 'TransitEncryptionEnabled' in conf['Properties'].keys() and 'AuthToken' in conf['Properties'].keys():
                if conf['Properties']['TransitEncryptionEnabled'] == True:
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = ElasticacheReplicationGroupEncryptionAtTransitAuthToken()
