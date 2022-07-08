resource "alicloud_db_instance" "pass" {
  engine                     = "MySQL"
  engine_version             = "5.6"
  instance_type              = "rds.mysql.t1.small"
  instance_storage           = "10"
  sql_collector_status       = "Enabled"
  sql_collector_config_value = 180
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
    }, {
    name  = "log_connections"
    value = "ON"
  }]
}

resource "alicloud_db_instance" "fail" {
  engine           = "MySQL"
  engine_version   = "5.6"
  instance_type    = "rds.mysql.t1.small"
  instance_storage = "10"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
    }, {
    name  = "log_connections"
    value = "ON"
  }]
}

resource "alicloud_db_instance" "fail2" {
  engine               = "MySQL"
  engine_version       = "5.6"
  instance_type        = "rds.mysql.t1.small"
  instance_storage     = "10"
  sql_collector_status = "Disabled"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
    }, {
    name  = "log_connections"
    value = "ON"
  }]
}

resource "alicloud_db_instance" "fail3" {
  engine               = "MySQL"
  engine_version       = "5.6"
  instance_type        = "rds.mysql.t1.small"
  instance_storage     = "10"
  sql_collector_status = "Enabled"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
    }, {
    name  = "log_connections"
    value = "ON"
  }]
}

resource "alicloud_db_instance" "fail4" {
  engine                     = "MySQL"
  engine_version             = "5.6"
  instance_type              = "rds.mysql.t1.small"
  instance_storage           = "10"
  sql_collector_status       = "Enabled"
  sql_collector_config_value = 30
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
    }, {
    name  = "log_connections"
    value = "ON"
  }]
}