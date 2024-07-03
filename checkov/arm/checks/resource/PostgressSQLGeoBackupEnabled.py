from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class PostgressSQLGeoBackupEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that PostgreSQL server enables geo-redundant backups"
        id = "CKV_AZURE_102"
        supported_resources = ['Microsoft.DBforPostgreSQL/servers']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> Any:
        return 'properties/storageProfile/geoRedundantBackup'

    def get_expected_value(self) -> str:
        return 'Enabled'


check = PostgressSQLGeoBackupEnabled()
