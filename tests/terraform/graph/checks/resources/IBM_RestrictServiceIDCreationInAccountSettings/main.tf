
# Case 1: Pass: as restrict_create_service_id  is set to "RESTRICTED"

resource "ibm_iam_account_settings" "pass" {
  restrict_create_service_id  = "RESTRICTED"
}

# Case 2: Fail: as restrict_create_service_id  is NOT set to "RESTRICTED"

resource "ibm_iam_account_settings" "fail_1" {
  restrict_create_service_id = "NOT_RESTRICTED"
}

# Case 3: Fail: as restrict_create_service_id  does not exist, By default, all members of an account can create service IDs

resource "ibm_iam_account_settings" "fail_2" {
  mfa                           = "LEVEL3"
  session_expiration_in_seconds = "40000"
}


