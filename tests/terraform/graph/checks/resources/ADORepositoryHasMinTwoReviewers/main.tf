resource "azuredevops_git_repository" "pass" {
  project_id = azuredevops_project.example.id
  name       = "Example Repository"
  initialization {
    init_type = "Clean"
  }
}

resource "azuredevops_branch_policy_min_reviewers" "example" {
  project_id = azuredevops_project.example.id

  enabled  = true
  blocking = true

  settings {
    reviewer_count                         = 7
    submitter_can_vote                     = false
    last_pusher_cannot_approve             = true
    allow_completion_with_rejects_or_waits = false
    on_push_reset_approved_votes           = true # OR on_push_reset_all_votes = true
    on_last_iteration_require_vote         = false

    scope {
      repository_id  = azuredevops_git_repository.pass.id
      repository_ref = azuredevops_git_repository.pass.default_branch
      match_type     = "Exact"
    }

    scope {
      repository_id  = null # All repositories in the project
      repository_ref = "refs/heads/releases"
      match_type     = "Prefix"
    }
  }
}


resource "azuredevops_git_repository" "fail" {
  project_id = azuredevops_project.example.id
  name       = "Example Repository"
  initialization {
    init_type = "Clean"
  }
}

resource "azuredevops_git_repository" "fail2" {
  project_id = azuredevops_project.example.id
  name       = "Example Repository"
  initialization {
    init_type = "Clean"
  }
}

resource "azuredevops_branch_policy_min_reviewers" "example" {
  project_id = azuredevops_project.example.id

  enabled  = true
  blocking = true

  settings {
    reviewer_count                         = 1
    submitter_can_vote                     = false
    last_pusher_cannot_approve             = true
    allow_completion_with_rejects_or_waits = false
    on_push_reset_approved_votes           = true # OR on_push_reset_all_votes = true
    on_last_iteration_require_vote         = false

    scope {
      repository_id  = azuredevops_git_repository.fail2.id
      repository_ref = azuredevops_git_repository.fail2.default_branch
      match_type     = "Exact"
    }

    scope {
      repository_id  = null # All repositories in the project
      repository_ref = "refs/heads/releases"
      match_type     = "Prefix"
    }
  }
}
