from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SQLDatabaseLedgerEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        Ledger helps protect data from any attacker or high-privileged user, including database administrators (DBAs),
        system administrators, and cloud administrators. As with a traditional ledger, the feature preserves
        historical data.
        If a row is updated in the database, its previous value is maintained and protected
        in a history table. Ledger provides a chronicle of all changes made to the database over time.
        Ledger and the historical data are managed transparently, offering protection without any application changes.
        The feature maintains historical data in a relational form to support SQL queries for auditing,
        forensics, and other purposes.
        It provides guarantees of cryptographic data integrity while maintaining the power, flexibility,
        and performance of the SQL database.

        Note that:
        - Ledger needs to be enabled at the deployment of the database and can't be removed once enabled
        - Ledger may come with performance impact, which means that it is advise to closely monitor
          the database performance in order to ensure that the database meets the performance objectives
        - Ledger comes with an additional cost, due to the data being stored

        """
        name = "Ensure that the Ledger feature is enabled on database that "
        name += "requires cryptographic proof and nonrepudiation of data integrity"
        id = "CKV_AZURE_224"
        supported_resources = ("azurerm_mssql_database",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "ledger_enabled"


check = SQLDatabaseLedgerEnabled()
