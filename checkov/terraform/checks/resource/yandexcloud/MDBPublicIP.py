from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class MDBPublicIP(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure public IP is not assigned to database cluster."
        id = "CKV_YC_12"
        categories = (CheckCategories.NETWORKING,)
        supported_resources = (
            "yandex_mdb_postgresql_cluster",
            "yandex_mdb_sqlserver_cluster",
            "yandex_mdb_mysql_cluster",
            "yandex_mdb_mongodb_cluster",
            "yandex_mdb_kafka_cluster",
            "yandex_mdb_greenplum_cluster",
            "yandex_mdb_elasticsearch_cluster",
            "yandex_mdb_clickhouse_cluster",
        )
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        if self.entity_type == "yandex_mdb_kafka_cluster":
            return "config/[0]/assign_public_ip"
        if self.entity_type == "yandex_mdb_greenplum_cluster":
            return "assign_public_ip"
        return "host/[0]/assign_public_ip"

    def get_forbidden_values(self) -> list[Any]:
        return [True]


check = MDBPublicIP()
