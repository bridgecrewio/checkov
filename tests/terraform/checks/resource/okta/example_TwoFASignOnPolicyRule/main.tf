resource "okta_app_signon_policy_rule" "fail" {
  policy_id                   = "someId"
  name                        = "Some Rule"
  factor_mode                 = "1FA"
  re_authentication_frequency = "PT43800H"
}

resource "okta_app_signon_policy_rule" "pass" {
  policy_id                   = "someId"
  name                        = "Some Rule"
  factor_mode                 = "2FA"
  re_authentication_frequency = "PT43800H"
}

# default is 2FA so missing factor_mode satisfies rule
resource "okta_app_signon_policy_rule" "pass2" {
  policy_id                   = "someId"
  name                        = "Some Rule"
  re_authentication_frequency = "PT43800H"
}
