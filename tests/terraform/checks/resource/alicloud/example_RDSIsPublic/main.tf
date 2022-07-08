resource "alicloud_db_instance" "fail" {
  engine              = "MySQL"
  engine_version      = "5.6"
  db_instance_class   = "rds.mysql.t1.small"
  db_instance_storage = "10"
  security_ips = [
    "0.0.0.0",
    "10.23.12.24/24"
  ]
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}

resource "alicloud_db_instance" "fail2" {
  engine              = "MySQL"
  engine_version      = "5.6"
  db_instance_class   = "rds.mysql.t1.small"
  db_instance_storage = "10"
  security_ips = [
    "0.0.0.0/0",
    "10.23.12.24/24"
  ]
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}

resource "alicloud_db_instance" "pass" {
  engine              = "MySQL"
  engine_version      = "5.6"
  db_instance_class   = "rds.mysql.t1.small"
  db_instance_storage = "10"
  security_ips = [
    "10.23.12.24"
  ]
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}


resource "alicloud_db_instance" "pass2" {
  engine              = "MySQL"
  engine_version      = "5.6"
  db_instance_class   = "rds.mysql.t1.small"
  db_instance_storage = "10"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}

