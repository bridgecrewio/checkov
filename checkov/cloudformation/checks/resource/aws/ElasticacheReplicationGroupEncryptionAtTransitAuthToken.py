from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ElasticacheReplicationGroupEncryptionAtTransitAuthToken(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the Elasticache Replication Group is securely encrypted at transit and has auth token"
        id = "CKV_AWS_31"
        supported_resources = ("AWS::ElastiCache::ReplicationGroup",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
            Looks for encryption configuration at aws_elasticache_replication_group:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html
        :param conf: aws_elasticache_replication_group configuration
        :return: <CheckResult>
        """
        properties = conf. get("Properties")
        if properties and isinstance(properties, dict):
            if "TransitEncryptionEnabled" in properties.keys() and "AuthToken" in properties.keys():
                if conf["Properties"]["TransitEncryptionEnabled"]:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticacheReplicationGroupEncryptionAtTransitAuthToken()
