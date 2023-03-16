resource "oci_core_network_security_group_security_rule" "pud_testnet" {
  network_security_group_id = oci_core_network_security_group.test_network_security_group.id
  protocol                  = "1"
  direction                 = "INGRESS"
  source                    = "0.0.0.0/0"
  stateless                 = true

  tcp_options {
    destination_port_range {
      min = 20
      max = 22
    }

    source_port_range {
      min = 100
      max = 100
    }
  }
}