# pass
resource "yandex_mdb_postgresql_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_sqlserver_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_redis_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_mysql_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_mongodb_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_kafka_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_greenplum_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_elasticsearch_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

resource "yandex_mdb_clickhouse_cluster" "pass" {
  name = "test-mdb"
  security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
}

# fail
resource "yandex_mdb_postgresql_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_sqlserver_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_redis_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_mysql_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_mongodb_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_kafka_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_greenplum_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_elasticsearch_cluster" "fail" {
  name = "test-mdb"
}

resource "yandex_mdb_clickhouse_cluster" "fail" {
  name = "test-mdb"
}