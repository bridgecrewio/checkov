
# Case 1: Pass: as MFA is configured

resource "ibm_iam_account_settings" "pass" {
    mfa                           = "LEVEL3"
    session_expiration_in_seconds = "40000"
    restrict_create_platform_apikey = "RESTRICTED" # checkov:skip=CKV_SECRET_6 test secret
}

# Case 2: Fail: as 'mfa' argument does NOT exist

resource "ibm_iam_account_settings" "fail_1" {
  restrict_create_platform_apikey = "NOT_RESTRICTED" # checkov:skip=CKV_SECRET_6 test secret
}

# Case 3: Fail: as 'mfa' equals to 'None'

resource "ibm_iam_account_settings" "fail_2" {
  mfa                           = "None"
  session_expiration_in_seconds = "40000"
}


