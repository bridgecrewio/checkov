
resource "github_actions_environment_secret" "fail" {
  environment       = "example_environment"
  secret_name       = "example_secret_name"
  plaintext_value   = "INTHECLEAR"
}


resource "github_actions_environment_secret" "pass" {
  environment       = "example_environment"
  secret_name       = "example_secret_name"
  encrypted_value   = "WOULDBEENCRYPTED"
}


resource "github_actions_organization_secret" "fail" {
  environment       = "example_environment"
  secret_name       = "example_secret_name"
  plaintext_value   = "INTHECLEAR"
}


resource "github_actions_organization_secret" "pass" {
  environment       = "example_environment"
  secret_name       = "example_secret_name"
  encrypted_value   = "WOULDBEENCRYPTED"
}


resource "github_actions_secret" "fail" {
  environment       = "example_environment"
  secret_name       = "example_secret_name"
  plaintext_value   = "INTHECLEAR"
}


resource "github_actions_secret" "pass" {
  environment       = "example_environment"
  secret_name       = "example_secret_name"
  encrypted_value   = "WOULDBEENCRYPTED"
}