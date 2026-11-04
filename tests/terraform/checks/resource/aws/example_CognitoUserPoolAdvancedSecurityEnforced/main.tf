resource "aws_cognito_user_pool" "pass" {
  name = "pass-pool"

  user_pool_add_ons {
    advanced_security_mode = "ENFORCED"
  }
}

resource "aws_cognito_user_pool" "fail_audit" {
  name = "fail-audit-pool"

  user_pool_add_ons {
    advanced_security_mode = "AUDIT"
  }
}

resource "aws_cognito_user_pool" "fail_off" {
  name = "fail-off-pool"

  user_pool_add_ons {
    advanced_security_mode = "OFF"
  }
}

resource "aws_cognito_user_pool" "fail_missing" {
  name = "fail-missing-pool"
}
