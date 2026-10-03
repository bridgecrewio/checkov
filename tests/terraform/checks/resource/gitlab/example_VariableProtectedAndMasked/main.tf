resource "gitlab_project_variable" "pass" {
  project   = "20"
  key       = "CI_SECRET"
  value     = "super-secret-value"
  protected = true
  masked    = true
}

resource "gitlab_group_variable" "pass" {
  group     = "5"
  key       = "CI_SECRET"
  value     = "super-secret-value"
  protected = true
  masked    = true
}

resource "gitlab_instance_variable" "pass" {
  key       = "CI_SECRET"
  value     = "super-secret-value"
  protected = true
  masked    = true
}

resource "gitlab_project_variable" "fail_unprotected" {
  project   = "20"
  key       = "CI_SECRET"
  value     = "super-secret-value"
  protected = false
  masked    = true
}

resource "gitlab_group_variable" "fail_unmasked" {
  group     = "5"
  key       = "CI_SECRET"
  value     = "super-secret-value"
  protected = true
  masked    = false
}

resource "gitlab_instance_variable" "fail_missing_both" {
  key   = "CI_SECRET"
  value = "super-secret-value"
}
