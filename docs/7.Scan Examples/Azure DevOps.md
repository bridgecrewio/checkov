---
layout: default
published: true
title: Azure DevOps configuration scanning
nav_order: 20
---

# Azure DevOps configuration scanning
Checkov supports the evaluation of policies on your Azure DevOps organization and repositories settings.
When using checkov with an Azure DevOps token it can collect your current org settings and validate it complies with Azure DevOps security best practices such as having a minimum of 2 approvals for a PR, not allowing the creator to approve his own PR and more.
Full list of Azure DevOps organization and repository settings related checks can be found  [here](https://www.checkov.io/5.Policy%20Index/azure_devops_configuration.html).

## Gitlab scanning configuration

| Environment Variable               | Default value       | Example                            | Description                                                                                                |
|------------------------------------|---------------------|------------------------------------|------------------------------------------------------------------------------------------------------------|
| CKV_AZURE_DEVOPS_CONFIG_FETCH_DATA | "True"              |                                    | checkov will try to fetch Azure DevOps configuration from API by default (unless no access token provided) |
| CKV_AZURE_DEVOPS_CONF_DIR_NAME     | "azure_devops_conf" |                                    | checkov will create a new directory named "azure_devops_conf" under current working directory              |
| SYSTEM_COLLECTIONURI               |                     | https://dev.azure.com/acme         | Azure DevOps organization URI                                                                              |
| SYSTEM_ACCESSTOKEN                 |                     | 1234567890                         | Azure DevOps personal access token to be used to fetch Azure DevOps configuration                          |
| SYSTEM_TEAMPROJECT                 |                     | example                            | Azure DevOps project name for which to fetch project configuration info                                    |
| BUILD_REPOSITORY_ID                |                     | 12345678-abcd-1234-abcd-1234567890 | Azure DevOps repository ID for which to fetch repository configuration info                                |
| SYSTEM_PULLREQUEST_TARGETBRANCH    |                     | refs/heads/main                    | Azure DevOps branch for which to fetch branch protection rules configuration                               |

### Example 'Minimum number of reviewers' policy configuration

```json
{
    "count": 1,
    "value": [
        {
            "createdBy": {
                "displayName": "Steve Rogers",
                "url": "https://spsprodweu5.vssps.visualstudio.com/12345678-abcd-1234-abcd-1234567890/_apis/Identities/12345678-abcd-1234-abcd-1234567890",
                "_links": {
                    "avatar": {
                        "href": "https://dev.azure.com/acme/_apis/GraphProfile/MemberAvatars/msa.example"
                    }
                },
                "id": "12345678-abcd-1234-abcd-1234567890",
                "uniqueName": "steve.rogers@marvel.com",
                "imageUrl": "https://dev.azure.com/acme/_api/_common/identityImage?id=12345678-abcd-1234-abcd-1234567890",
                "descriptor": "msa.example"
            },
            "createdDate": "2022-12-18T23:27:31.6259462Z",
            "isEnabled": true,
            "isBlocking": true,
            "isDeleted": false,
            "settings": {
                "minimumApproverCount": 1,
                "creatorVoteCounts": false,
                "allowDownvotes": false,
                "resetOnSourcePush": false,
                "requireVoteOnLastIteration": false,
                "resetRejectionsOnSourcePush": false,
                "blockLastPusherVote": false,
                "scope": [
                    {
                        "refName": "refs/heads/main",
                        "matchKind": "Exact",
                        "repositoryId": "12345678-abcd-1234-abcd-1234567890"
                    }
                ]
            },
            "isEnterpriseManaged": false,
            "_links": {
                "self": {
                    "href": "https://dev.azure.com/acme/12345678-abcd-1234-abcd-1234567890/_apis/policy/configurations/3"
                },
                "policyType": {
                    "href": "https://dev.azure.com/acme/12345678-abcd-1234-abcd-1234567890/_apis/policy/types/fa4e907d-c16b-4a4c-9dfa-4906e5d171dd"
                }
            },
            "revision": 6,
            "id": 3,
            "url": "https://dev.azure.com/acme/12345678-abcd-1234-abcd-1234567890/_apis/policy/configurations/3",
            "type": {
                "id": "fa4e907d-c16b-4a4c-9dfa-4906e5d171dd",
                "url": "https://dev.azure.com/acme/12345678-abcd-1234-abcd-1234567890/_apis/policy/types/fa4e907d-c16b-4a4c-9dfa-4906e5d171dd",
                "displayName": "Minimum number of reviewers"
            }
        }
    ]
}

```

### Example policy

```python
from __future__ import annotations

from checkov.azure_devops.checks.base_policy_check import BasePolicyCheck


class CreatorApproval(BasePolicyCheck):
    def __init__(self) -> None:
        name = "Ensure pull request creators are not allowed to approve their own changes"
        id = "CKV_AZUREDEVOPS_2"
        super().__init__(
            name=name,
            id=id,
            policy_type_id="fa4e907d-c16b-4a4c-9dfa-4906e5d171dd",  # Minimum number of reviewers
        )

    def get_evaluated_keys(self) -> list[str]:
        return ["settings/creatorVoteCounts"]

    def get_expected_value(self) -> bool:
        return False


check = CreatorApproval()

```

### Running in CLI

```bash
# configure Azure DevOps connection 
export SYSTEM_COLLECTIONURI="https://dev.azure.com/acme"
export SYSTEM_ACCESSTOKEN="1234567890"
export SYSTEM_TEAMPROJECT="example"
export BUILD_REPOSITORY_ID="12345678-abcd-1234-abcd-1234567890"
export SYSTEM_PULLREQUEST_TARGETBRANCH="refs/heads/main"

checkov -d . --framework azure_devops_configuration
```

### Example output

```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By bridgecrew.io | version: 2.2.180 


azure_devops_configuration scan results:

Passed checks: 1, Failed checks: 1, Skipped checks: 0

Check: CKV_AZUREDEVOPS_2: "Ensure pull request creators are not allowed to approve their own changes"
	PASSED for resource: /azure_devops_conf/policies.json.*./azure_devops_conf/policies.json.CKV_AZUREDEVOPS_2
	File: /policies.json:1-100
Check: CKV_AZUREDEVOPS_1: "Ensure any change to code receives approval of two strongly authenticated users"
	FAILED for resource: /azure_devops_conf/policies.json.*./azure_devops_conf/policies.json.CKV_AZUREDEVOPS_1
	File: /policies.json:1-100

		Code lines for this resource are too many. Please use IDE of your choice to review the file.


Process finished with exit code 1

```
