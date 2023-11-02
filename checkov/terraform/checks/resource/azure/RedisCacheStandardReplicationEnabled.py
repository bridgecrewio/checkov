from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RedisCacheStandardReplicationEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        With Standard Replication, Azure Cache for Redis has a high availability architecture
        that ensures your managed instance is functioning, even when outages affect
        the underlying virtual machines (VMs). Whether the outage is planned or unplanned outages,
        Azure Cache for Redis delivers greater percentage availability rates than what's attainable
        by hosting Redis on a single VM.

        An Azure Cache for Redis in the applicable tiers runs on a pair of Redis servers by default.
        The two servers are hosted on dedicated VMs.
        Open-source Redis allows only one server to handle data write requests.
        """
        name = "Standard Replication should be enabled"
        id = "CKV_AZURE_230"
        supported_resources = ("azurerm_redis_cache",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "sku_name"

    def get_expected_values(self) -> list[Any]:
        return ["Standard", "Premium"]


check = RedisCacheStandardReplicationEnabled()
