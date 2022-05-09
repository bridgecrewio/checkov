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
