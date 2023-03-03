resource "alicloud_mongodb_instance" "fail" {
  engine_version      = "3.4"
  db_instance_class   = "dds.mongo.mid"
  db_instance_storage = 10
  vswitch_id          = alicloud_vswitch.ditch.id
  security_ip_list    = ["0.0.0.0/0","10.168.1.12", "100.69.7.112"]
  kms_encryption_context= {

  }
  # tde_status = "Disabled"
  # not set
}

resource "alicloud_mongodb_instance" "fail2" {
  engine_version      = "3.4"
  db_instance_class   = "dds.mongo.mid"
  db_instance_storage = 10
  vswitch_id          = alicloud_vswitch.ditch.id
  security_ip_list    = ["0.0.0.0/0","10.168.1.12", "100.69.7.112"]
  kms_encryption_context= {

  }
  # tde_status = "Disabled"
  ssl_action = "Close"
  # not set
  network_type = "Classic"
}

resource "alicloud_mongodb_instance" "pass" {
  engine_version      = "3.4"
  db_instance_class   = "dds.mongo.mid"
  db_instance_storage = 10
  vswitch_id          = alicloud_vswitch.ditch.id
  security_ip_list    = ["0.0.0.0/0","10.168.1.12", "100.69.7.112"]
  kms_encryption_context= {

  }
  # tde_status = "Disabled"
  ssl_action = "Open"
  # not set
  network_type = "VPC"
}

resource "alicloud_mongodb_instance" "pass2" {
  engine_version      = "3.4"
  db_instance_class   = "dds.mongo.mid"
  db_instance_storage = 10
  vswitch_id          = alicloud_vswitch.ditch.id
  security_ip_list    = ["0.0.0.0/0","10.168.1.12", "100.69.7.112"]
  kms_encryption_context= {

  }
  # tde_status = "Disabled"
  ssl_action = "Update"
  # not set
  network_type = "VPC"
}
resource "alicloud_vswitch" "ditch" {
  vpc_id     = "anyoldtripe"
  cidr_block = "0.0.0.0/0"
}