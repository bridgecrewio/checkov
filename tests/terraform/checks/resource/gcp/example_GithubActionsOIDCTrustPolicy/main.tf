# pass1 - Basic valid configuration
resource "google_iam_workload_identity_pool_provider" "pass1" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-1"
  display_name                       = "GitHub Actions Provider"
  description                        = "OIDC identity pool provider for GitHub Actions gggg"
  disabled                          = false
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  attribute_condition               = "assertion.sub == 'repo:myOrg/myRepo:*'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# pass2 - Valid configuration with specific branch reference
resource "google_iam_workload_identity_pool_provider" "pass2" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-2"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == 'repo:myOrg/myRepo:ref:refs/heads/main'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# pass3 - Valid configuration with double equals
resource "google_iam_workload_identity_pool_provider" "pass3" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-3"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == 'repo:myOrg/myRepo:ref:refs/heads/main'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# pass4 - Valid configuration with org-only repo pattern
resource "google_iam_workload_identity_pool_provider" "pass_org_only" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-4"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == 'repo:myOrg/valid-repo:*'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# fail1 - Missing attribute condition
resource "google_iam_workload_identity_pool_provider" "fail1" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-fail-1"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# fail2 - Invalid claim format
resource "google_iam_workload_identity_pool_provider" "fail2" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-fail-2"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == 'invalid'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# fail3 - Wildcard in condition
resource "google_iam_workload_identity_pool_provider" "fail_wildcard" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-fail-3"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == '*'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# fail4 - Using abusable claim
resource "google_iam_workload_identity_pool_provider" "fail_abusable" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-fail-4"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == 'workflow:github-actions:repo:myOrg/myRepo:ref:refs/heads/main'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# fail5 - Wildcard assertion in repo pattern
resource "google_iam_workload_identity_pool_provider" "fail_wildcard_assertion" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-fail-5"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == 'repo:*'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}

# fail6 - Misused repo pattern
resource "google_iam_workload_identity_pool_provider" "fail_misused_repo" {
  workload_identity_pool_id          = "example-pool"
  workload_identity_pool_provider_id = "example-provider-fail-6"
  attribute_mapping                 = {
    "google.subject"       = "assertion.sub"
  }
  attribute_condition               = "assertion.sub == 'repo:myOrg*'"
  issuer_uri                       = "https://token.actions.githubusercontent.com"
}
