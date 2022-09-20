resource "oci_identity_policy" "example" {
    compartment_id = var.tenancy_id
    statements = ["allow group group-admin-001 to use groups in tenancy where target.group.name != 'Administrators'"]
}
