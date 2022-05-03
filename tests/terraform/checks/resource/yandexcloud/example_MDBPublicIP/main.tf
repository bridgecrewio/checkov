# pass
resource "yandex_mdb_postgresql_cluster" "pass" {
  name = "test-mdb"
  host {
    assign_public_ip = false
  }
}

resource "yandex_mdb_sqlserver_cluster" "pass" {
  name = "test-mdb"
  host {
    assign_public_ip = false
  }
}

resource "yandex_mdb_mysql_cluster" "pass" {
  name = "test-mdb"
  host {
    assign_public_ip = false
  }
}

resource "yandex_mdb_mongodb_cluster" "pass" {
  name = "test-mdb"
  host {
    assign_public_ip = false
  }
}

resource "yandex_mdb_kafka_cluster" "pass" {
  name = "test-mdb"
  config {
    assign_public_ip = false
  }
}

resource "yandex_mdb_greenplum_cluster" "pass" {
  name = "test-mdb"
  assign_public_ip = false
}

resource "yandex_mdb_elasticsearch_cluster" "pass" {
  name = "test-mdb"
  host {
    assign_public_ip = false
  }
}

resource "yandex_mdb_clickhouse_cluster" "pass" {
  name = "test-mdb"
  host {
    assign_public_ip = false
  }
}

# fail
resource "yandex_mdb_postgresql_cluster" "fail" {
  name = "test-mdb"
  host {
    assign_public_ip = true
  }
}

resource "yandex_mdb_sqlserver_cluster" "fail" {
  name = "test-mdb"
  host {
    assign_public_ip = true
  }
}

resource "yandex_mdb_mysql_cluster" "fail" {
  name = "test-mdb"
  host {
    assign_public_ip = true
  }
}

resource "yandex_mdb_mongodb_cluster" "fail" {
  name = "test-mdb"
  host {
    assign_public_ip = true
  }
}

resource "yandex_mdb_kafka_cluster" "fail" {
  name = "test-mdb"
  config {
    assign_public_ip = true
  }
}

resource "yandex_mdb_greenplum_cluster" "fail" {
  name = "test-mdb"
  assign_public_ip = true
}

resource "yandex_mdb_elasticsearch_cluster" "fail" {
  name = "test-mdb"
  host {
    assign_public_ip = true
  }
}

resource "yandex_mdb_clickhouse_cluster" "fail" {
  name = "test-mdb"
  host {
    assign_public_ip = true
  }
}