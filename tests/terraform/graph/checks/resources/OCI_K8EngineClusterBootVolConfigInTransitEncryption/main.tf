# PASS: is_pv_encryption_in_transit_enabled is TRUE

resource "oci_containerengine_node_pool" "pass" {

  node_config_details {
    is_pv_encryption_in_transit_enabled = true
  }
}

# FAIL 1: is_pv_encryption_in_transit_enabled is FALSE

resource "oci_containerengine_node_pool" "fail_1" {

  node_config_details {

  is_pv_encryption_in_transit_enabled = false

  }

}

# FAIL 2: node_config_details block doesn't contain is_pv_encryption_in_transit_enabled argument

resource "oci_containerengine_node_pool" "fail_2" {

  node_config_details {

    kms_key_id = oci_kms_key.pud_test_key.id

  }

}
