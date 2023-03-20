# PASS case 1: It passes because source is NOT 0.0.0.0/0

resource "oci_core_network_security_group_security_rule" "pass_1" {
  network_security_group_id = oci_core_network_security_group.fail_network_security_group.id
  protocol                  = "1"
  direction                 = "INGRESS"
  source                    = "192.168.12.0/0"
  stateless                 = true

  tcp_options {
    destination_port_range {
      min = 3389
      max = 3391
    }

    source_port_range {
      min = 100
      max = 100
    }
  }
}

# PASS case 2: It passes because destination port range does not include port 3389

resource "oci_core_network_security_group_security_rule" "pass_2" {
  network_security_group_id = oci_core_network_security_group.fail_network_security_group.id
  protocol                  = "6"
  direction                 = "INGRESS"
  source                    = "0.0.0.0/0"
  stateless                 = true

  tcp_options {
    destination_port_range {
      min = 3390
      max = 3391
    }

    source_port_range {
      min = 100
      max = 100
    }
  }
}

# FAIL case 1: 
# Protocol should not be 1, source should not be 0.0.0.0/0
# tcp_options.destination_port_range.min should NOT be less than or equals to 3389

resource "oci_core_network_security_group_security_rule" "fail_1" {
  network_security_group_id = oci_core_network_security_group.fail_network_security_group.id
  protocol                  = "1"
  direction                 = "INGRESS"
  source                    = "0.0.0.0/0"
  stateless                 = true

  tcp_options {
    destination_port_range {
      min = 3387
      max = 3391
    }

    source_port_range {
      min = 100
      max = 100
    }
  }
}


# FAIL case 2: 
# source should not be 0.0.0.0/0
# tcp_options.destination_port_range.min should NOT be less than or equals to 3389

resource "oci_core_network_security_group_security_rule" "fail_2" {
  network_security_group_id = oci_core_network_security_group.fail_network_security_group.id
  protocol                  = "6"
  direction                 = "INGRESS"
  source                    = "0.0.0.0/0"
  stateless                 = true

  tcp_options {
    destination_port_range {
      min = 3389
      max = 3389
    }

    source_port_range {
      min = 100
      max = 100
    }
  }
}


