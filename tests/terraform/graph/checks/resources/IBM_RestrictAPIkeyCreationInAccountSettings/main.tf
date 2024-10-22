
# Case 1: Pass: as restrict_create_platform_apikey  is set to "RESTRICTED"

resource "ibm_iam_account_settings" "pass" {
  restrict_create_platform_apikey = "RESTRICTED" # checkov:skip=CKV_SECRET_6 test secret
}

# Case 2: Fail: as restrict_create_platform_apikey  is NOT set to "RESTRICTED"

resource "ibm_iam_account_settings" "fail_1" {
  restrict_create_platform_apikey = "NOT_RESTRICTED" # checkov:skip=CKV_SECRET_6 test secret
}

# Case 3: Fail: as restrict_create_platform_apikey  does not exist, By default, all members of an account can create API keys

resource "ibm_iam_account_settings" "fail_2" {
  mfa                           = "LEVEL3"
  session_expiration_in_seconds = "40000"
}


