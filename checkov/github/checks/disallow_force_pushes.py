from checkov.github.base_github_branch_security import BranchSecurity


class GithubBranchDisallowForcePushes(BranchSecurity):
    def __init__(self):
        name = "Ensure GitHub branch protection rules does not allow force pushes"
        id = "CKV_GITHUB_5"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self):
        return ['allow_force_pushes/enabled']

    def get_expected_value(self):
        return False


check = GithubBranchDisallowForcePushes()
