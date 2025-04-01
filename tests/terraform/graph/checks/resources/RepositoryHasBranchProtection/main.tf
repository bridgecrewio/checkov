resource "github_branch_protection" "resource" {
  repository_id = github_repository.pass.node_id
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

resource "github_repository" "pass" {
  name = "test"
}

resource "github_repository" "fail" {
  name = "fail"
}

resource "github_repository" "pass2" {
  name = "test2"
}

resource "github_branch_protection_v3" "example" {
  repository     = github_repository.pass2.name
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

#pass

resource "github_repository" "pass_ruleset" {
  name        = "example"
  description = "Example repository"
}

resource "github_repository_ruleset" "pass_ruleset" {
  name        = "example"
  repository  = github_repository.pass_ruleset.name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~ALL"]
      exclude = []
    }
  }

  bypass_actors {
    actor_id    = 13473
    actor_type  = "Integration"
    bypass_mode = "always"
  }

  rules {
    creation                = true
    update                  = true
    deletion                = true
    required_linear_history = true
    required_signatures     = true

    required_deployments {
      required_deployment_environments = ["test"]
    }


  }
}