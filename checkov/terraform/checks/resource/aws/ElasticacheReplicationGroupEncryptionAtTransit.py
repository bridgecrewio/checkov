from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class ElasticacheReplicationGroupEncryptionAtTransit(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticache Replication Group  is securely encrypted at transit"
        id = "CKV_AWS_30"
        supported_resources = ['aws_elasticache_replication_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_elasticache_replication_group:
            https://www.terraform.io/docs/providers/aws/r/elasticache_replication_group.html
        :param conf: aws_elasticache_replication_group configuration
        :return: <CheckResult>
        """
        if "transit_encryption_enabled" in conf.keys():
            if conf["transit_encryption_enabled"][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticacheReplicationGroupEncryptionAtTransit()
