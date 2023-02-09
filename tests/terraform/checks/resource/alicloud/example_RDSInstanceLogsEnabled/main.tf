resource "alicloud_db_instance" "fail" {
  engine           = "MySQL"
  engine_version   = "5.6"
  instance_type    = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status       = "Disabled"
  auto_upgrade_minor_version = "Manual"
  # ssl_action="Closed"
  security_ips = [
    "0.0.0.0",
    "10.23.12.24/24"
  ]
  parameters {
    name  = "innodb_large_prefix"
    value = "ON"
  }
  parameters {
    name  = "connect_timeout"
    value = "50"
  }
}

resource "alicloud_db_instance" "fail2" {
  engine           = "MySQL"
  engine_version   = "5.6"
  instance_type    = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status       = "Disabled"
  auto_upgrade_minor_version = "Manual"
  # ssl_action="Closed"
  security_ips = [
    "0.0.0.0",
    "10.23.12.24/24"
  ]
}

resource "alicloud_db_instance" "fail3" {
  engine           = "MySQL"
  engine_version   = "5.6"
  instance_type    = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status       = "Disabled"
  auto_upgrade_minor_version = "Manual"
  # ssl_action="Closed"
  security_ips = [
    "0.0.0.0",
    "10.23.12.24/24"
  ]
  parameters {
        name = "log_duration"
        value = "OFF"
    }
}

resource "alicloud_db_instance" "pass" {
  engine           = "MySQL"
  engine_version   = "5.6"
  instance_type    = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status       = "Disabled"
  auto_upgrade_minor_version = "Manual"
  # ssl_action="Closed"
  security_ips = [
    "0.0.0.0",
    "10.23.12.24/24"
  ]
  parameters {
        name = "log_duration"
        value = "ON"
    }
}

resource "alicloud_db_instance" "pass2" {
  engine           = "MySQL"
  engine_version   = "5.6"
  instance_type    = "rds.mysql.t1.small"
  instance_storage = "10"
  tde_status       = "Disabled"
  auto_upgrade_minor_version = "Manual"
  # ssl_action="Closed"
  security_ips = [
    "0.0.0.0",
    "10.23.12.24/24"
  ]
  parameters {
        name = "log_duration"
        value = "on"
    }
}