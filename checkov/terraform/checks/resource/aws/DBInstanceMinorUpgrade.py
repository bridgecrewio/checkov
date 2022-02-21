from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DBInstanceMinorUpgrade(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DB instance gets all minor upgrades automatically"
        id = "CKV_AWS_226"
        supported_resources = ["aws_db_instance", 'aws_rds_cluster_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "auto_minor_version_upgrade"


check = DBInstanceMinorUpgrade()
