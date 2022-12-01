
resource "oci_core_network_security_group_security_rule" "pass" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "EGRESS"
    protocol = "all"
    source = "0.0.0.0/0"

    tcp_options {
        destination_port_range {
            max = 22
            min = 22
        }
    }
}

resource "oci_core_network_security_group_security_rule" "pass1" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "EGRESS"
    protocol = "all"
    source = "0.0.0.0/0"
}

resource "oci_core_network_security_group_security_rule" "pass2" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "INGRESS"
    protocol = "all"
    source = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"

    tcp_options {
        destination_port_range {
            max = 25
            min = 25
        }
    }
}

resource "oci_core_network_security_group_security_rule" "pass3" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "INGRESS"
    protocol = "all"
    source = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"

    tcp_options {
        destination_port_range {
            max = 21
            min = 1
        }
    }
}


resource "oci_core_network_security_group_security_rule" "fail" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "INGRESS"
    protocol = "all"
    source = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"

    tcp_options {
        destination_port_range {
            max = 22
            min = 22
        }
    }
}

resource "oci_core_network_security_group_security_rule" "fail1" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "INGRESS"
    protocol = "all"
    source = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"

    tcp_options {
        destination_port_range {
            max = 25
            min = 21
        }
    }
}

resource "oci_core_network_security_group_security_rule" "fail2" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "INGRESS"
    protocol = "all"
    source = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"
}


resource "oci_core_network_security_group_security_rule" "fail3" {
    network_security_group_id = oci_core_network_security_group.sg.id
    direction = "INGRESS"
    protocol = "all"
    source = "0.0.0.0/0"
    source_type = "CIDR_BLOCK"

    tcp_options {
        destination_port_range {
            max = 25
            min = 21
        }
    }
}
