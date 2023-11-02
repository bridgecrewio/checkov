from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class MySQLGeoBackupEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that My SQL server enables geo-redundant backups"
        id = "CKV_AZURE_94"
        supported_resources = ("Microsoft.DBforMySQL/flexibleServers",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/Backup/geoRedundantBackup"


check = MySQLGeoBackupEnabled()
