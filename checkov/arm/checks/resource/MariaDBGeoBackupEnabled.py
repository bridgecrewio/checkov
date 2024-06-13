from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class MariaDBGeoBackupEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that MariaDB server enables geo-redundant backups"
        id = "CKV_AZURE_129"
        supported_resources = ("Microsoft.DBforMariaDB/servers",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/storageProfile/geoRedundantBackup"

    def get_expected_value(self) -> str:
        return "Enabled"


check = MariaDBGeoBackupEnabled()
