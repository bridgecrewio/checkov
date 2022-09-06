from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AuroraEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in Aurora is securely encrypted at rest"
        id = "CKV_AWS_96"
        supported_resources = ("AWS::RDS::DBCluster",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, dict[str, Any]]) -> CheckResult:
        # If you specify the SnapshotIdentifier or SourceDBInstanceIdentifier property, don't specify this property.
        # The value is inherited from the snapshot or source DB instance.
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-storageencrypted
        # Doc refers to 'SourceDBInstanceIdentifier' but that is not an available field. This is a doc error. 'SourceDBClusterIdentifier' is correct.
        properties = conf.get("Properties")
        if properties:
            if "SnapshotIdentifier" in properties.keys() or "SourceDBClusterIdentifier" in properties.keys():
                return CheckResult.UNKNOWN
        # No snapshot or source DB; Use base class implementation
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "Properties/StorageEncrypted"


check = AuroraEncryption()
