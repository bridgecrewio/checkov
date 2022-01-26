resource "oci_core_security_list" "pass" {
  compartment_id = oci_identity_compartment.tf-compartment.id
  vcn_id         = oci_core_vcn.test_vcn.id
  ingress_security_rules {
    protocol = "all"
    source   = "192.168.1.0/24"
  }
}

resource "oci_core_security_list" "pass2" {
  compartment_id = oci_identity_compartment.tf-compartment.id
  vcn_id         = oci_core_vcn.test_vcn.id
  ingress_security_rules {
    protocol  = "all"
    source    = "192.168.1.0/24"
    stateless = true
  }
}

resource "oci_core_security_list" "pass3" {
  compartment_id = oci_identity_compartment.tf-compartment.id
  vcn_id         = oci_core_vcn.test_vcn.id

  ingress_security_rules {
    description = "First"
    protocol    = "all"
    source      = "192.168.1.0/24"
    stateless   = true
  }

  ingress_security_rules {
    description = "Second"
    protocol    = var.ingress["protocol"]
    source      = var.ingress["source"]
    stateless   = true
  }

}

resource "oci_core_security_list" "fail" {
  compartment_id = oci_identity_compartment.tf-compartment.id
  vcn_id         = oci_core_vcn.test_vcn.id
  ingress_security_rules {
    protocol  = "all"
    source    = "192.168.1.0/24"
    stateless = false
  }
}

resource "oci_core_security_list" "fail2" {
  compartment_id = oci_identity_compartment.tf-compartment.id
  vcn_id         = oci_core_vcn.test_vcn.id

  ingress_security_rules {
    description = "First"
    protocol    = "all"
    source      = "192.168.1.0/24"
    stateless   = true
  }

  ingress_security_rules {
    description = "Second"
    protocol    = var.ingress["protocol"]
    source      = var.ingress["source"]
    stateless   = false
  }

}

resource "oci_core_security_list" "skipped" {
  compartment_id = oci_identity_compartment.tf-compartment.id
  vcn_id         = oci_core_vcn.test_vcn.id
}