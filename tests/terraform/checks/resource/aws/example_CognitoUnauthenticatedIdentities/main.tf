resource "aws_cognito_identity_pool" "pass" {
  allow_unauthenticated_identities = false
}

resource "aws_cognito_identity_pool" "fail" {
  allow_unauthenticated_identities = true
}
