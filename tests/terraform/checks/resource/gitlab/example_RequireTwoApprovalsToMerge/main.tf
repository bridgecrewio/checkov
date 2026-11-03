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
resource "gitlab_project" "pass_new" {
  name = "example-new"
}

resource "gitlab_project_approval_rule" "pass_new" {
  project            = gitlab_project.pass_new.id
  name               = "reviewers"
  approvals_required = 2
}

resource "gitlab_project" "fail_new" {
  name = "example-new"
}

resource "gitlab_project_approval_rule" "fail_new" {
  project            = gitlab_project.fail_new.id
  name               = "reviewers"
  approvals_required = 1
}

# No approval rule of its own: the rule attached to pass_new must not
# make this project pass.
resource "gitlab_project" "fail_other" {
  name = "example-new"
}
