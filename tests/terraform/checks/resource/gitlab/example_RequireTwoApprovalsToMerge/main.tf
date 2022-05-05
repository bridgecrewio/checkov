resource "gitlab_project" "fail" {
  name = "example-two"

  push_rules {
    author_email_regex     = "@example\\.com$"
    commit_committer_check = true
    member_check           = true
    prevent_secrets        = true
  }
}

resource "gitlab_project" "fail2" {
  name = "example-two"
  approvals_before_merge = 1
  push_rules {
    author_email_regex     = "@example\\.com$"
    commit_committer_check = true
    member_check           = true
    prevent_secrets        = true
  }
}

resource "gitlab_project" "pass" {
  name = "example-two"
  approvals_before_merge = 2

  push_rules {
    author_email_regex     = "@example\\.com$"
    commit_committer_check = true
    member_check           = true
    prevent_secrets        = true
  }
}