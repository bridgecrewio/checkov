# pass1 - sub plus repository_id (Microsoft documented example)
resource "azuread_application_flexible_federated_identity_credential" "pass1" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "pass1"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://token.actions.githubusercontent.com"
  claims_matching_expression = "claims['sub'] matches 'repo:octo-org/octo-repo:ref:refs/heads/*' and claims['repository_id'] eq '456789'"
}

# pass2 - immutable sub plus both immutable claims
resource "azuread_application_flexible_federated_identity_credential" "pass2" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "pass2"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://token.actions.githubusercontent.com"
  claims_matching_expression = "claims['sub'] matches 'repo:octo-org@123456/octo-repo@456789:*' and claims['repository_id'] eq '456789' and claims['repository_owner_id'] eq '123456'"
}

# pass3 - owner-level trust bound by repository_owner_id
resource "azuread_application_flexible_federated_identity_credential" "pass3" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "pass3"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://token.actions.githubusercontent.com"
  claims_matching_expression = "claims['sub'] matches 'repo:octo-org/*' and claims['repository_owner_id'] eq '123456'"
}

# pass_non_github - other issuers are out of scope for this check
resource "azuread_application_flexible_federated_identity_credential" "pass_non_github" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "pass_non_github"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://app.terraform.io"
  claims_matching_expression = "claims['sub'] matches 'organization:octo-org:project:*:workspace:*:run_phase:*'"
}

# fail1 - sub and job_workflow_ref, but no immutable claim
resource "azuread_application_flexible_federated_identity_credential" "fail1" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "fail1"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://token.actions.githubusercontent.com"
  claims_matching_expression = "claims['sub'] matches 'repo:octo-org/octo-repo:ref:refs/heads/*' and claims['job_workflow_ref'] matches 'octo-org/octo-repo/.github/workflows/*.yml@refs/heads/main'"
}

# fail2 - sub only
resource "azuread_application_flexible_federated_identity_credential" "fail2" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "fail2"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://token.actions.githubusercontent.com"
  claims_matching_expression = "claims['sub'] matches 'repo:octo-org/octo-repo:*'"
}

# fail3 - immutable claim without sub
resource "azuread_application_flexible_federated_identity_credential" "fail3" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "fail3"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://token.actions.githubusercontent.com"
  claims_matching_expression = "claims['repository_id'] eq '456789'"
}

# fail4 - repository_id only supports eq
resource "azuread_application_flexible_federated_identity_credential" "fail4" {
  application_id             = "/applications/00000000-0000-0000-0000-000000000000"
  display_name               = "fail4"
  audience                   = "api://AzureADTokenExchange"
  issuer                     = "https://token.actions.githubusercontent.com"
  claims_matching_expression = "claims['sub'] matches 'repo:octo-org/octo-repo:*' and claims['repository_id'] matches '4567*'"
}
