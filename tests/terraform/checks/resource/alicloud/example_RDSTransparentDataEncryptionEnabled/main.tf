resource "alicloud_db_instance" "pass" {
  engine              = "MySQL"
  engine_version      = "5.6"
  instance_type   = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status          = "Enabled"
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
  instance_type   = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status          = "Disabled"
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
  engine_version      = "8.0"
  instance_type   = "rds.mysql.t1.small"
  instance_storage = "10"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}

resource "alicloud_db_instance" "pass2" {
  engine              = "SQLServer"
  engine_version      = "2019_std_ha"
  instance_type   = "mssql.x4.medium.e1"
  instance_storage = "10"
  tde_status          = "Enabled"
  parameters          = []
}

resource "alicloud_db_instance" "unknown" {
  engine              = "MySQL"
  engine_version      = "5.5"
  instance_type   = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status          = "Enabled"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}

resource "alicloud_db_instance" "unknown3" {
  engine              = "PostgreSQL"
  engine_version      = "9.4"
  instance_type   = "rds.pg.s1.small"
  instance_storage = "10"
  tde_status          = "Enabled"
  parameters = [{
    name  = "innodb_large_prefix"
    value = "ON"
    }, {
    name  = "connect_timeout"
    value = "50"
  }]
}