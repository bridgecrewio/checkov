resource "gitlab_project" "pass" {
  name = "example-two"

  push_rules {
    author_email_regex     = "@example\\.com$"
    commit_committer_check = true
    member_check           = true
    prevent_secrets        = true
  }
}

resource "gitlab_project" "fail" {
  name        = "example"
  description = "My awesome codebase"

  visibility_level = "public"
}

resource "gitlab_project" "fail2" {
  name = "example-two"

  push_rules {
    author_email_regex     = "@example\\.com$"
    commit_committer_check = true
    member_check           = true
    prevent_secrets        = false
  }
}

resource "gitlab_project" "pass_new" {
  name = "example-new"
}

resource "gitlab_project_push_rules" "pass_new" {
  project         = gitlab_project.pass_new.id
  prevent_secrets = true
}

resource "gitlab_project" "fail_new" {
  name = "example-new"
}

resource "gitlab_project_push_rules" "fail_new" {
  project         = gitlab_project.fail_new.id
  prevent_secrets = false
}

# No push rules of its own: the rules attached to pass_new must not
# make this project pass.
resource "gitlab_project" "fail_other" {
  name = "example-new"
}
