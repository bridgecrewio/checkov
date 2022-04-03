
resource "oci_core_network_security_group_security_rule" "pass" {
  network_security_group_id = oci_core_network_security_group.test_network_security_group.id
  direction                 = "INGRESS"
  protocol                  = var.network_security_group_security_rule_protocol
  stateless                 = true
}

resource "oci_core_network_security_group_security_rule" "fail" {
  network_security_group_id = oci_core_network_security_group.test_network_security_group.id
  direction                 = "INGRESS"
  protocol                  = var.network_security_group_security_rule_protocol
  stateless                 = false
}

resource "oci_core_network_security_group_security_rule" "fail1" {
  network_security_group_id = oci_core_network_security_group.test_network_security_group.id
  direction                 = "INGRESS"
  protocol                  = var.network_security_group_security_rule_protocol
}

resource "oci_core_network_security_group_security_rule" "skip" {
  network_security_group_id = oci_core_network_security_group.test_network_security_group.id
  direction                 = "EGRESS"
  protocol                  = var.network_security_group_security_rule_protocol
  stateless                 = true
}

resource "oci_core_network_security_group_security_rule" "skip1" {
  network_security_group_id = oci_core_network_security_group.test_network_security_group.id
  direction                 = "EGRESS"
  protocol                  = var.network_security_group_security_rule_protocol
  stateless                 = false
}
