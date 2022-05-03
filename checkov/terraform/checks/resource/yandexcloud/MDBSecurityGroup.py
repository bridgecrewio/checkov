from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE

class MDBSecurityGroup(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure security group is assigned to database cluster."
        id = "CKV_YC_1"
        supported_resources = [
            "yandex_mdb_postgresql_cluster",
            "yandex_mdb_sqlserver_cluster",
            "yandex_mdb_redis_cluster",
            "yandex_mdb_mysql_cluster",
            "yandex_mdb_mongodb_cluster",
            "yandex_mdb_kafka_cluster",
            "yandex_mdb_greenplum_cluster",
            "yandex_mdb_elasticsearch_cluster",
            "yandex_mdb_clickhouse_cluster",
        ]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "security_group_ids"

    def get_expected_value(self):
        return ANY_VALUE
    
check = MDBSecurityGroup()