# pass1 - Basic valid configuration with federated credential
resource "azuread_application_federated_identity_credential" "pass1" {
  application_object_id = "example-app-id"
  display_name         = "github-actions-oidc"
  description          = "GitHub Actions OIDC"
  audiences           = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:myOrg/myRepo:environment:Production"
}

# pass2 - Valid configuration with specific branch reference
resource "azuread_application_federated_identity_credential" "pass2" {
  application_object_id = "example-app-id"
  display_name         = "github-actions-oidc"
  audiences           = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:myOrg/myRepo:ref:refs/heads/main"
}

# pass4 - Valid configuration with org-only repo pattern
resource "azuread_application_federated_identity_credential" "pass4" {
  application_object_id = "example-app-id"
  display_name         = "github-actions-oidc"
  audiences           = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:myOrg/valid-repo:*"
}

# fail1 - Missing subject
resource "azuread_application_federated_identity_credential" "fail1" {
  application_object_id = "example-app-id"
  display_name         = "github-actions-oidc"
  audiences           = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
}

# fail2 - Invalid claim format
resource "azuread_application_federated_identity_credential" "fail2" {
  application_object_id = "example-app-id"
  display_name         = "github-actions-oidc"
  audiences           = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "invalid"
}

# fail3 - Wildcard in subject
resource "azuread_application_federated_identity_credential" "fail3" {
  application_object_id = "example-app-id"
  display_name         = "github-actions-oidc"
  audiences           = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "*"
}

# fail5 - Wildcard assertion in repo pattern
resource "azuread_application_federated_identity_credential" "fail5" {
  application_object_id = "example-app-id"
  display_name         = "github-actions-oidc"
  audiences           = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:*"
}
