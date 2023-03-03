resource "ncloud_access_control_group_rule" "pass" {
  access_control_group_no = ncloud_access_control_group.acg.id

  inbound {
    protocol    = "TCP"
    ip_block    = "0.0.0.0/0"
    port_range  = "22"
    description = "accept 22 port"
  }

  outbound {
    protocol    = "TCP"
    ip_block    = "10.0.3.0/16" 
    port_range  = "1-65535"
    description = "accept 1-65535 port"
  }
}

resource "ncloud_access_control_group_rule" "fail" {
  access_control_group_no = ncloud_access_control_group.acg.id

  inbound {
    protocol    = "TCP"
    ip_block    = "10.0.3.0/16"
    port_range  = "22"
    description = "accept 22 port"
  }

  outbound {
    protocol    = "TCP"
    ip_block    = "0.0.0.0/0" 
    port_range  = "1-65535"
    description = "accept 1-65535 port"
  }
}

resource "ncloud_access_control_group_rule" "fail1" {
  access_control_group_no = ncloud_access_control_group.acg.id

  inbound {
    protocol    = "TCP"
    ip_block    = "10.16.0.0/32" 
    port_range  = "1-65535"
    description = "accept 1-65535 port"
  }

  outbound {
    protocol    = "TCP"
    ip_block    = "::/0"
    port_range  = "22"
    description = "accept 22 port"
  }
}