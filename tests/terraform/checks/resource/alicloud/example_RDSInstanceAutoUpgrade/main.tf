resource "alicloud_db_instance" "fail" {
  auto_upgrade_minor_version = "Manual"
  engine               = "MySQL"
  engine_version       = "5.6"
  instance_type        = "rds.mysql.s2.large"
  instance_storage     = "30"
  instance_charge_type = "Postpaid"
  instance_name        = "myfirstdb"
  vswitch_id           = alicloud_vswitch.ditch.id
  monitoring_period    = "60"
  ssl_action           = "Close"
}

resource "alicloud_vswitch" "ditch" {
  vpc_id     = "anyoldtripe"
  cidr_block = "0.0.0.0/0"
}

resource "alicloud_db_instance" "fail2" {
  engine               = "MySQL"
  engine_version       = "5.6"
  instance_type        = "rds.mysql.s2.large"
  instance_storage     = "30"
  instance_charge_type = "Postpaid"
  instance_name        = "myfirstdb"
  vswitch_id           = alicloud_vswitch.ditch.id
  monitoring_period    = "60"
  ssl_action           = "Close"
}

resource "alicloud_db_instance" "pass" {
  auto_upgrade_minor_version = "Auto"
  engine               = "MySQL"
  engine_version       = "5.6"
  instance_type        = "rds.mysql.s2.large"
  instance_storage     = "30"
  instance_charge_type = "Postpaid"
  instance_name        = "myfirstdb"
  vswitch_id           = alicloud_vswitch.ditch.id
  monitoring_period    = "60"
  ssl_action           = "Close"
}