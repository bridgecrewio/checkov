# Test Case TLDR:
# Users in groups:
#   admin_group:
#       user1 (has api key)
#       user2 (no api key)
#   non_admin_group:
#       user3 (no api key)
# Users not in a group:
#   user4 (no api key)


resource "oci_identity_user" "user1" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.user_description"
    name = "user1"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    email = "var.user_email"
    freeform_tags = {"Department"= "Finance"}
}

resource "oci_identity_user" "user2" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.user_description"
    name = "user2"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    email = "var.user_email"
    freeform_tags = {"Department"= "Finance"}
}

resource "oci_identity_user" "user3" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.user_description"
    name = "user3"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    email = "var.user_email"
    freeform_tags = {"Department"= "Finance"}
}

resource "oci_identity_user" "user4" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.user_description"
    name = "user3"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    email = "var.user_email"
    freeform_tags = {"Department"= "Finance"}
}


resource "oci_identity_group" "admin_group" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.group_description"
    name = "Administrators"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    freeform_tags = {"Department"= "Finance"}
}


resource "oci_identity_group" "non_admin_group" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.group_description"
    name = "NotAdministrators"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    freeform_tags = {"Department"= "Finance"}
}


resource "oci_identity_api_key" "user1_api_key" {
    #Required
    key_value = "var.api_key_key_value"
    user_id = oci_identity_user.user1.id
}


resource "oci_identity_user_group_membership" "user1_in_admin_group" {
    #Required
    group_id = oci_identity_group.admin_group.id
    user_id = oci_identity_user.user1.id
}


resource "oci_identity_user_group_membership" "user2_in_admin_group" {
    #Required
    group_id = oci_identity_group.admin_group.id
    user_id = oci_identity_user.user2.id
}


resource "oci_identity_user_group_membership" "user3_in_non_admin_group" {
    #Required
    group_id = oci_identity_group.non_admin_group.id
    user_id = oci_identity_user.user3.id
}

