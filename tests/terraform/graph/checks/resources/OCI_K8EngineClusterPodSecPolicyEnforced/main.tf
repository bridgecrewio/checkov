# PASS: 

resource "oci_containerengine_cluster" "pass" {

  options {
    admission_controller_options {
      is_pod_security_policy_enabled = "True"
    }
    persistent_volume_config {
      freeform_tags = {
        "ClusName" = pud_cluster
      }
    }
  }
  vcn_id = oci_core_vcn.pud_oci_core_vcn.id
}

# FAIL 1: is_pod_security_policy_enabled should NOT equals to FALSE

resource "oci_containerengine_cluster" "fail_1" {

  options {
    admission_controller_options {
      is_pod_security_policy_enabled = "False"
    }
    persistent_volume_config {
      freeform_tags = {
        "ClusName" = pud_cluster
      }
    }
  }
  vcn_id = oci_core_vcn.pud_oci_core_vcn.id
}

# FAIL 2: is_pod_security_policy_enabled argument does NOT exist

resource "oci_containerengine_cluster" "fail_2" {

  options {

    persistent_volume_config {
      freeform_tags = {
        "ClusName" = pud_cluster
      }
    }
  }
  vcn_id = oci_core_vcn.pud_oci_core_vcn.id
}


