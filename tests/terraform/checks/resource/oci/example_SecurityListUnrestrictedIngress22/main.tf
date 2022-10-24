resource "oci_core_security_list" "fail1" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "var.security_list_ingress_security_rules_protocol"
        source = "0.0.0.0/0"

        tcp_options {
            max = 22
            min = 22
            source_port_range {
                max = "var.security_list_ingress_security_rules_tcp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_tcp_options_source_port_range_min"
            }
        }
        udp_options {
            max = 900
            min = 7
            source_port_range {
                max = "var.security_list_ingress_security_rules_udp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_udp_options_source_port_range_min"
            }
        }
    }
}

resource "oci_core_security_list" "fail" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "var.security_list_ingress_security_rules_protocol"
        source = "0.0.0.0/0"

        tcp_options {
            max = 25
            min = 25
            source_port_range {
                max = "var.security_list_ingress_security_rules_tcp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_tcp_options_source_port_range_min"
            }
        }
        udp_options {
            max = 22
            min = 22
            source_port_range {
                max = "var.security_list_ingress_security_rules_udp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_udp_options_source_port_range_min"
            }
        }
    }
}

resource "oci_core_security_list" "pass0" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "var.security_list_ingress_security_rules_protocol"
        source = "0.0.0.0/0"

        tcp_options {
            max = 25
            min = 25
            source_port_range {
                max = "var.security_list_ingress_security_rules_tcp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_tcp_options_source_port_range_min"
            }
        }
        udp_options {
            max = 21
            min = 20
            source_port_range {
                max = "var.security_list_ingress_security_rules_udp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_udp_options_source_port_range_min"
            }
        }
    }
}

resource "oci_core_security_list" "fail2" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "var.security_list_ingress_security_rules_protocol"
        source = "0.0.0.0/0"

        tcp_options {
            max = 22
            min = 21
            source_port_range {
                max = "var.security_list_ingress_security_rules_tcp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_tcp_options_source_port_range_min"
            }
        }
        udp_options {
            max = 23
            min = 20
            source_port_range {
                max = "var.security_list_ingress_security_rules_udp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_udp_options_source_port_range_min"
            }
        }
    }
}
resource "oci_core_security_list" "fail3" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "all"
        source = "0.0.0.0/0"
    }
}
resource "oci_core_security_list" "pass1" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "1"
        source = "0.0.0.0/0"
    }
}
resource "oci_core_security_list" "pass4" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "all"
        source = "0.0.0.1/0"
    }
}
resource "oci_core_security_list" "fail5" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"
}

resource "oci_core_security_list" "pass5" {
  ingress_security_rules = [
    {
      protocol = "1"
      source   = "${var.external_icmp_ingress}"

      icmp_options {
        "type" = 3
        "code" = 4
      }
    },
    {
      protocol = "1"
      source   = "${var.internal_icmp_ingress}"

      icmp_options {
        "type" = 3
        "code" = 4
      }
    }
  ]

  provisioner "local-exec" {
    command = "sleep 5"
  }
    compartment_id = ""
    vcn_id         = ""
}


resource "oci_core_security_list" "pass6" {
    compartment_id = "var.compartment_id"
    vcn_id = "oci_core_vcn.test_vcn.id"

    ingress_security_rules {
        protocol = "var.security_list_ingress_security_rules_protocol"
        source = "0.0.0.0/0"

        tcp_options {
            max = "25"
            min = "25"
            source_port_range {
                max = "var.security_list_ingress_security_rules_tcp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_tcp_options_source_port_range_min"
            }
        }
        udp_options {
            max = "21"
            min = "20"
            source_port_range {
                max = "var.security_list_ingress_security_rules_udp_options_source_port_range_max"
                min = "var.security_list_ingress_security_rules_udp_options_source_port_range_min"
            }
        }
    }
}