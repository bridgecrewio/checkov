---
layout: default
title: github_configuration resource scans
nav_order: 1
---

# github_configuration resource scans (auto generated)

|    |               | Id                   | Type   | Entity                                                                           | Policy               | IaC                                                                                                           |
|----|---------------|----------------------|--------|----------------------------------------------------------------------------------|----------------------|---------------------------------------------------------------------------------------------------------------|
|  0 | CKV_GITHUB_1  | github_configuration | *      | Ensure GitHub organization security settings require 2FA                         | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/2fa.py                              |
|  1 | CKV_GITHUB_2  | github_configuration | *      | Ensure GitHub organization security settings require SSO                         | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/sso.py                              |
|  2 | CKV_GITHUB_3  | github_configuration | *      | Ensure GitHub organization security settings has IP allow list enabled           | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/ipallowlist.py                      |
|  3 | CKV_GITHUB_4  | github_configuration | *      | Ensure GitHub branch protection rules requires signed commits                    | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_signatures.py               |
|  4 | CKV_GITHUB_5  | github_configuration | *      | Ensure GitHub branch protection rules does not allow force pushes                | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/disallow_force_pushes.py            |
|  5 | CKV_GITHUB_6  | github_configuration | *      | Ensure GitHub organization webhooks are using HTTPS                              | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/webhooks_https_orgs.py              |
|  6 | CKV_GITHUB_7  | github_configuration | *      | Ensure GitHub repository webhooks are using HTTPS                                | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/webhooks_https_repos.py             |
|  7 | CKV_GITHUB_8  | github_configuration | *      | Ensure GitHub branch protection rules requires linear history                    | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_linear_history.py           |
|  8 | CKV_GITHUB_9  | github_configuration | *      | Ensure 2 admins are set for each repository                                      | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/repository_collaborators.py         |
|  9 | CKV_GITHUB_10 | github_configuration | *      | Ensure branch protection rules are enforced on administrators                    | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/enforce_branch_protection_admins.py |
| 10 | CKV_GITHUB_11 | github_configuration | *      | Ensure GitHub branch protection dismisses stale review on new commit - CIS 1.1.4 | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/dismiss_stale_reviews.py            |
| 11 | CKV_GITHUB_12 | github_configuration | *      | Ensure GitHub branch protection restricts who can dismiss PR reviews - CIS 1.1.5 | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/restrict_pr_review_dismissal.py     |
| 12 | CKV_GITHUB_13 | github_configuration | *      | Ensure GitHub branch protection requires CODEOWNER reviews - CIS 1.1.6           | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_code_owner_reviews.py       |
| 13 | CKV_GITHUB_14 | github_configuration | *      | Ensure GitHub branch protection requires status checks - CIS 1.1.9               | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_status_checks_pr.py         |
| 14 | CKV_GITHUB_16 | github_configuration | *      | Ensure GitHub branch protection requires conversation resolution - CIS 1.1.11    | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_conversation_resolution.py  |
| 15 | CKV_GITHUB_17 | github_configuration | *      | Ensure GitHub branch protection requires push restrictions - CIS 1.1.15          | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/require_push_restrictions.py        |
| 16 | CKV_GITHUB_18 | github_configuration | *      | Ensure GitHub branch protection rules does not allow deletions - CIS 1.1.17      | github_configuration | https://github.com/bridgecrewio/checkov/tree/master/checkov/github/checks/disallow_branch_deletions.py        |


---


