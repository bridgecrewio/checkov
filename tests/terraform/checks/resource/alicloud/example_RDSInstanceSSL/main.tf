resource "alicloud_db_instance" "pass" {
  engine              = "MySQL"
  engine_version      = "5.6"
  ssl_action          = "Open"
  instance_storage    = "30"
  instance_type       = "mysql.n2.small.25"
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
  ssl_action          = "Update"
  instance_storage    = "30"
  instance_type       = "mysql.n2.small.25"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}

resource "alicloud_db_instance" "fail" {
  engine              = "MySQL"
  engine_version      = "5.6"
  ssl_action          = "Close"
  instance_storage    = "30"
  instance_type       = "mysql.n2.small.25"
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
  instance_type   = "rds.mysql.t1.small"
  instance_storage = "10"
  instance_storage    = "30"
  instance_type       = "mysql.n2.small.25"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}


