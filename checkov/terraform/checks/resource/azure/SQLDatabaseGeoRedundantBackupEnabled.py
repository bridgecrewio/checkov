from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SQLDatabaseGeoRedundantBackupEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that backups are geo-redundants for Azure SQL Databases"
        id = "CKV_AZURE_241"
        supported_resources = ("azurerm_mssql_database",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "storage_account_type"
    
    def get_expected_value(self):
        return 'Geo'

check = SQLDatabaseGeoRedundantBackupEnabled()
