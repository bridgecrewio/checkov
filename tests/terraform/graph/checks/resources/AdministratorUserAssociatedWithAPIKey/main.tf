#Test Case TLDR:
#group_pass:
#        user1 (has api key)
#        user2 (has api key)
#
#group_fail:
#        user1 (has api key)
#        user3 (no api key)


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


resource "oci_identity_group" "group_pass" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.group_description"
    name = "Administrators"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    freeform_tags = {"Department"= "Finance"}
}


resource "oci_identity_group" "group_fail" {
    #Required
    compartment_id = "var.tenancy_ocid"
    description = "var.group_description"
    name = "Administrators"

    #Optional
    defined_tags = {"Operations.CostCenter"= "42"}
    freeform_tags = {"Department"= "Finance"}
}


resource "oci_identity_api_key" "user1_api_key" {
    #Required
    key_value = "var.api_key_key_value"
    user_id = oci_identity_user.user1.id
}

resource "oci_identity_api_key" "user2_api_key" {
    #Required
    key_value = "var.api_key_key_value"
    user_id = oci_identity_user.user2.id
}


resource "oci_identity_user_group_membership" "user1_in_group_pass" {
    #Required
    group_id = oci_identity_group.group_pass.id
    user_id = oci_identity_user.user1.id
}


resource "oci_identity_user_group_membership" "user2_in_group_pass" {
    #Required
    group_id = oci_identity_group.group_pass.id
    user_id = oci_identity_user.user2.id
}


resource "oci_identity_user_group_membership" "user3_in_group_fail" {
    #Required
    group_id = oci_identity_group.group_fail.id
    user_id = oci_identity_user.user3.id
}


resource "oci_identity_user_group_membership" "user1_in_group_fail" {
    #Required
    group_id = oci_identity_group.group_fail.id
    user_id = oci_identity_user.user1.id
}

