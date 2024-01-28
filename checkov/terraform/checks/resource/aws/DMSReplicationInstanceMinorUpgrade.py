from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DMSReplicationInstanceMinorUpgrade(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DMS replication instance gets all minor upgrade automatically"
        id = "CKV_AWS_222"
        supported_resources = ["aws_dms_replication_instance"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "auto_minor_version_upgrade"


check = DMSReplicationInstanceMinorUpgrade()
