resource "oci_file_storage_file_system" "pass" {
  availability_domain = var.file_system_availability_domain
  compartment_id      = var.compartment_id

  defined_tags       = { "Operations.CostCenter" = "42" }
  display_name       = var.file_system_display_name
  freeform_tags      = { "Department" = "Finance" }
  kms_key_id         = oci_kms_key.test_key.id
  source_snapshot_id = oci_file_storage_snapshot.test_snapshot.id
}


resource "oci_file_storage_file_system" "fail" {
  availability_domain = var.file_system_availability_domain
  compartment_id      = var.compartment_id

  defined_tags       = { "Operations.CostCenter" = "42" }
  display_name       = var.file_system_display_name
  freeform_tags      = { "Department" = "Finance" }
  source_snapshot_id = oci_file_storage_snapshot.test_snapshot.id
}