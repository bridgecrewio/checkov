from __future__ import annotations

from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class SQLServerUsesADAuth(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        """
        I think that this check is really, ensure that only AD auth is used (not user/pass)
        """

        name = "Ensure Azure AD authentication is enabled for Azure SQL (MSSQL)"
        id = "CKV2_AZURE_27"
        supported_resources = ["Microsoft.Sql/servers"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/administratorLogin'

    def get_forbidden_values(self) -> list[Any]:
        return [ANY_VALUE]


check = SQLServerUsesADAuth()
