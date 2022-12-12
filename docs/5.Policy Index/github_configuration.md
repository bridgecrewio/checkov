---
layout: default
title: github_configuration resource scans
nav_order: 1
---

# github_configuration resource scans (auto generated)

|    |               | Id                   | Type   | Entity                                                                          | Policy               | IaC                                                                                                           |
|----|---------------|----------------------|--------|---------------------------------------------------------------------------------|----------------------|---------------------------------------------------------------------------------------------------------------|
|  0 | CKV_GITHUB_1  | github_configuration | *      | Ensure GitHub organization security settings require 2FA                        | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/2fa.py                              |
|  1 | CKV_GITHUB_2  | github_configuration | *      | Ensure GitHub organization security settings require SSO                        | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/sso.py                              |
|  2 | CKV_GITHUB_3  | github_configuration | *      | Ensure GitHub organization security settings has IP allow list enabled          | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/ipallowlist.py                      |
|  3 | CKV_GITHUB_4  | github_configuration | *      | Ensure GitHub branch protection rules requires signed commits                   | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_signatures.py               |
|  4 | CKV_GITHUB_5  | github_configuration | *      | Ensure GitHub branch protection rules does not allow force pushes               | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/disallow_force_pushes.py            |
|  5 | CKV_GITHUB_6  | github_configuration | *      | Ensure GitHub organization webhooks are using HTTPS                             | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/webhooks_https_orgs.py              |
|  6 | CKV_GITHUB_7  | github_configuration | *      | Ensure GitHub repository webhooks are using HTTPS                               | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/webhooks_https_repos.py             |
|  7 | CKV_GITHUB_8  | github_configuration | *      | Ensure GitHub branch protection rules requires linear history                   | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_linear_history.py           |
|  8 | CKV_GITHUB_9  | github_configuration | *      | Ensure 2 admins are set for each repository                                     | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/repository_collaborators.py         |
|  9 | CKV_GITHUB_10 | github_configuration | *      | Ensure branch protection rules are enforced on administrators                   | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/enforce_branch_protection_admins.py |
| 10 | CKV_GITHUB_11 | github_configuration | *      | Ensure GitHub branch protection dismisses stale review on new commit            | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/dismiss_stale_reviews.py            |
| 11 | CKV_GITHUB_12 | github_configuration | *      | Ensure GitHub branch protection restricts who can dismiss PR reviews            | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/restrict_pr_review_dismissal.py     |
| 12 | CKV_GITHUB_13 | github_configuration | *      | Ensure GitHub branch protection requires CODEOWNER reviews                      | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_code_owner_reviews.py       |
| 13 | CKV_GITHUB_14 | github_configuration | *      | Ensure all checks have passed before the merge of new code                      | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_status_checks_pr.py         |
| 14 | CKV_GITHUB_15 | github_configuration | *      | Ensure inactive branches are reviewed and removed periodically                  | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/disallow_inactive_branch_60days.py  |
| 15 | CKV_GITHUB_16 | github_configuration | *      | Ensure GitHub branch protection requires conversation resolution                | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_conversation_resolution.py  |
| 16 | CKV_GITHUB_17 | github_configuration | *      | Ensure GitHub branch protection requires push restrictions                      | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_push_restrictions.py        |
| 17 | CKV_GITHUB_18 | github_configuration | *      | Ensure GitHub branch protection rules does not allow deletions                  | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/disallow_branch_deletions.py        |
| 18 | CKV_GITHUB_19 | github_configuration | *      | Ensure any change to code receives approval of two strongly authenticated users | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_2approvals.py               |
| 19 | CKV_GITHUB_20 | github_configuration | *      | Ensure open git branches are up to date before they can be merged into codebase | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_updated_branch_pr.py        |


---


