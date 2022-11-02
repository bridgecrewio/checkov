resource "ncloud_network_acl_rule" "pass" {
  network_acl_no    = ncloud_network_acl.nacl.id

  inbound {
    priority    = 110
    protocol    = "TCP"
    rule_action = "ALLOW"
    deny_allow_group_no = ncloud_network_acl_deny_allow_group.deny_allow_group.id
    port_range  = "22"
  }
}

resource "ncloud_network_acl_rule" "pass1" {
  network_acl_no    = ncloud_network_acl.nacl.id

  inbound {
    priority    = 110
    protocol    = "TCP"
    rule_action = "ALLOW"
    deny_allow_group_no = ncloud_network_acl_deny_allow_group.deny_allow_group.id
    port_range  = "1-43"
  }
}

resource "ncloud_network_acl_rule" "fail" {
  network_acl_no    = ncloud_network_acl.nacl.id

  inbound {
    priority    = 110
    protocol    = "TCP"
    rule_action = "ALLOW"
    deny_allow_group_no = ncloud_network_acl_deny_allow_group.deny_allow_group.id
  }
}

resource "ncloud_network_acl_rule" "fail1" {
  network_acl_no    = ncloud_network_acl.nacl.id

  inbound {
    priority    = 110
    protocol    = "TCP"
    rule_action = "ALLOW"
    deny_allow_group_no = ncloud_network_acl_deny_allow_group.deny_allow_group.id
    port_range  = "1-65535"
  }
}