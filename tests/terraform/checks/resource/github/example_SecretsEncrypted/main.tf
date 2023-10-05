
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

resource "github_actions_organization_secret" "pass_empty_value" {
  environment       = "example_environment"
  secret_name       = "example_secret_name"
  encrypted_value   = "WOULDBEENCRYPTED"
  plaintext_value   = ""
}

# value ref

resource "azuread_service_principal_password" "gh_actions" {
  service_principal_id = azuread_service_principal.gh_actions.object_id
}

resource "github_actions_secret" "value_ref" {
  repository       = "example_repository"
  secret_name      = "example_secret_name"
  plaintext_value  = azuread_service_principal_password.gh_actions.value
}
