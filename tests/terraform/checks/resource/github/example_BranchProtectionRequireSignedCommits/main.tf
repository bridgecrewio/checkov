resource "github_branch_protection_v3" "fail" {
  repository     = github_repository.example.name
  branch         = "main"
  enforce_admins = true

  required_status_checks {
    strict   = false
    contexts = ["ci/travis"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews = true
    dismissal_users       = ["foo-user"]
    dismissal_teams       = [github_team.example.slug]
  }

  restrictions {
    users = ["foo-user"]
    teams = [github_team.example.slug]
    apps  = ["foo-app"]
  }
}

resource "github_branch_protection_v3" "fail2" {
  repository     = github_repository.example.name
  branch         = "main"
  enforce_admins = true
  require_signed_commits = false

  required_status_checks {
    strict   = false
    contexts = ["ci/travis"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews = true
    dismissal_users       = ["foo-user"]
    dismissal_teams       = [github_team.example.slug]
    required_approving_review_count = 1
  }

  restrictions {
    users = ["foo-user"]
    teams = [github_team.example.slug]
    apps  = ["foo-app"]
  }
}

resource "github_branch_protection_v3" "pass" {
  repository     = github_repository.example.name
  branch         = "main"
  enforce_admins = true
  require_signed_commits = true
  required_status_checks {
    strict   = false
    contexts = ["ci/travis"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews = true
    dismissal_users       = ["foo-user"]
    dismissal_teams       = [github_team.example.slug]
    required_approving_review_count = 2
  }

  restrictions {
    users = ["foo-user"]
    teams = [github_team.example.slug]
    apps  = ["foo-app"]
  }
}


resource "github_branch_protection" "fail" {
  repository_id = github_repository.example.node_id
  # also accepts repository name
  # repository_id  = github_repository.example.name

  pattern          = "main"
  enforce_admins   = true
  allows_deletions = true

  required_status_checks {
    strict   = false
    contexts = ["ci/travis"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews  = true
    restrict_dismissals    = true
    dismissal_restrictions = [
      data.github_user.example.node_id,
      github_team.example.node_id,
    ]
  }

  push_restrictions = [
    data.github_user.example.node_id,
    # limited to a list of one type of restriction (user, team, app)
    # github_team.example.node_id
  ]

}


resource "github_branch_protection" "fail2" {
  repository_id = github_repository.example.node_id
  # also accepts repository name
  # repository_id  = github_repository.example.name

  pattern          = "main"
  enforce_admins   = true
  allows_deletions = true
  require_signed_commits = false
  required_status_checks {
    strict   = false
    contexts = ["ci/travis"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews  = true
    restrict_dismissals    = true
    dismissal_restrictions = [
      data.github_user.example.node_id,
      github_team.example.node_id,
    ]
    required_approving_review_count = 1
  }

  push_restrictions = [
    data.github_user.example.node_id,
    # limited to a list of one type of restriction (user, team, app)
    # github_team.example.node_id
  ]

}

resource "github_branch_protection" "pass" {
  repository_id = github_repository.example.node_id
  # also accepts repository name
  # repository_id  = github_repository.example.name

  pattern          = "main"
  enforce_admins   = true
  allows_deletions = true
  require_signed_commits = true

  required_status_checks {
    strict   = false
    contexts = ["ci/travis"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews  = true
    restrict_dismissals    = true
    dismissal_restrictions = [
      data.github_user.example.node_id,
      github_team.example.node_id,
    ]
    required_approving_review_count = 1
  }

  push_restrictions = [
    data.github_user.example.node_id,
    # limited to a list of one type of restriction (user, team, app)
    # github_team.example.node_id
  ]

}