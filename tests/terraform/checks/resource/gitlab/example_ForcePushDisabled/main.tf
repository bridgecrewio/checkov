resource "gitlab_branch_protection" "pass" {
  project                      = "12345"
  branch                       = "BranchProtected"
  push_access_level            = "developer"
  merge_access_level           = "developer"
  unprotect_access_level       = "developer"
  allow_force_push             = false
  code_owner_approval_required = true
  allowed_to_push {
    user_id = 5
  }
  allowed_to_push {
    user_id = 521
  }
  allowed_to_merge {
    user_id = 15
  }
  allowed_to_merge {
    user_id = 37
  }
  allowed_to_unprotect {
    user_id = 15
  }
  allowed_to_unprotect {
    group_id = 42
  }
}

resource "gitlab_branch_protection" "pass2" {
  project                      = "12345"
  branch                       = "BranchProtected"
  push_access_level            = "developer"
  merge_access_level           = "developer"
  unprotect_access_level       = "developer"
  code_owner_approval_required = true
  allowed_to_push {
    user_id = 5
  }
  allowed_to_push {
    user_id = 521
  }
  allowed_to_merge {
    user_id = 15
  }
  allowed_to_merge {
    user_id = 37
  }
  allowed_to_unprotect {
    user_id = 15
  }
  allowed_to_unprotect {
    group_id = 42
  }
}

resource "gitlab_branch_protection" "fail" {
  project                      = "12345"
  branch                       = "BranchProtected"
  push_access_level            = "developer"
  merge_access_level           = "developer"
  unprotect_access_level       = "developer"
  allow_force_push             = true
  code_owner_approval_required = true
  allowed_to_push {
    user_id = 5
  }
  allowed_to_push {
    user_id = 521
  }
  allowed_to_merge {
    user_id = 15
  }
  allowed_to_merge {
    user_id = 37
  }
  allowed_to_unprotect {
    user_id = 15
  }
  allowed_to_unprotect {
    group_id = 42
  }
}
