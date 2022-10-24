resource "oci_core_volume" "pass" {
  #Required
  compartment_id = var.compartment_id

  #Optional
  availability_domain = var.volume_availability_domain
  backup_policy_id    = data.oci_core_volume_backup_policies.test_volume_backup_policies.volume_backup_policies.0.id
  block_volume_replicas {
    #Required
    availability_domain = var.volume_block_volume_replicas_availability_domain

    #Optional
    display_name = var.volume_block_volume_replicas_display_name
  }
  defined_tags         = { "Operations.CostCenter" = "42" }
  display_name         = var.volume_display_name
  freeform_tags        = { "Department" = "Finance" }
  is_auto_tune_enabled = var.volume_is_auto_tune_enabled
  kms_key_id           = oci_kms_key.test_key.id
  size_in_gbs          = var.volume_size_in_gbs
  size_in_mbs          = var.volume_size_in_mbs
  source_details {
    #Required
    id   = var.volume_source_details_id
    type = var.volume_source_details_type
  }
  vpus_per_gb                    = var.volume_vpus_per_gb
  block_volume_replicas_deletion = true
}


resource "oci_core_volume" "fail" {
  #Required
  compartment_id = var.compartment_id

  #Optional
  availability_domain = var.volume_availability_domain

  block_volume_replicas {
    #Required
    availability_domain = var.volume_block_volume_replicas_availability_domain

    #Optional
    display_name = var.volume_block_volume_replicas_display_name
  }
  defined_tags         = { "Operations.CostCenter" = "42" }
  display_name         = var.volume_display_name
  freeform_tags        = { "Department" = "Finance" }
  is_auto_tune_enabled = var.volume_is_auto_tune_enabled
  kms_key_id           = oci_kms_key.test_key.id
  size_in_gbs          = var.volume_size_in_gbs
  size_in_mbs          = var.volume_size_in_mbs
  source_details {
    #Required
    id   = var.volume_source_details_id
    type = var.volume_source_details_type
  }
  vpus_per_gb                    = var.volume_vpus_per_gb
  block_volume_replicas_deletion = true
}