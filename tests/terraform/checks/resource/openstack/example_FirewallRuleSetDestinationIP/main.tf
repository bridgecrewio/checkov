resource "openstack_fw_rule_v1" "fail" {
  name             = "my_rule_world"
  description      = "let anyone in"
  action           = "allow"
  protocol         = "tcp"
  destination_port = "22"
  enabled          = "true"
  # destination_ip_address = "10.0.0.1"
}

resource "openstack_fw_rule_v1" "fail-cidr" {
  name                   = "my_small_world"
  description            = "let anyone in"
  action                 = "allow"
  protocol               = "tcp"
  destination_port       = "22"
  enabled                = "true"
  destination_ip_address = "0.0.0.0/0"
}

resource "openstack_fw_rule_v1" "pass" {
  name                   = "my_small_world"
  description            = "let anyone in"
  action                 = "allow"
  protocol               = "tcp"
  destination_port       = "22"
  enabled                = "true"
  destination_ip_address = "10.0.0.1"
}
