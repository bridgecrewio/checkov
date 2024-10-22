---
layout: default
published: true
title: Gitlab configuration scanning
nav_order: 20
---

# Gitlab configuration scanning
Checkov supports the evaluation of policies on your Gitlab organization and repositories settings.
When using checkov with Gitlab token it can collect your current org settings and validate it complies with Gitlab security best practices such as having 2FA defined, having SSO and more.
Full list of gitlab organization and repository settings related checks can be found  [here](https://www.checkov.io/5.Policy%20Index/gitlab_configuration.html).

## Gitlab scanning configuration

| Environment Variable          | Default value     | Description    |
|-------------|----------|-------------------------------------------|
| CKV_GITLAB_CONFIG_FETCH_DATA| "True" | checkov will try to fetch Gitlab configuration from API by default (unless no access token provided)  |
| CKV_GITLAB_CONF_DIR_NAME   | "gitlab_conf" | checkov will create a new directory named "gitlab_conf" under current working directory                          |
| CI_SERVER_URL   | "https://gitlab.com/" |  |
| CI_JOB_TOKEN   |  | Gitlab personal access token to be used to fetch Gitlab configuration |

### Example groups configuration

```json
[
  {
    "id": 15483421,
    "web_url": "https://gitlab.com/groups/baraktest1",
    "name": "baraktestgroup",
    "path": "baraktest1",
    "description": "",
    "visibility": "private",
    "share_with_group_lock": false,
    "require_two_factor_authentication": false,
    "two_factor_grace_period": 48,
    "project_creation_level": "developer",
    "auto_devops_enabled": null,
    "subgroup_creation_level": "maintainer",
    "emails_disabled": null,
    "mentions_disabled": null,
    "lfs_enabled": true,
    "default_branch_protection": 2,
    "avatar_url": null,
    "request_access_enabled": true,
    "full_name": "baraktestgroup",
    "full_path": "baraktest1",
    "created_at": "2022-01-17T11:03:19.763Z",
    "parent_id": null,
    "ldap_cn": null,
    "ldap_access": null
  }
]
```

### Example policy

```python
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.gitlab.base_gitlab_configuration_check import BaseGitlabCheck
from checkov.gitlab.schemas.groups import schema
from checkov.json_doc.enums import BlockType


class GroupsTwoFactorAuthentication(BaseGitlabCheck):
    def __init__(self):
        name = "Ensure all Gitlab groups require two factor authentication"
        id = "CKV_GITLAB_2"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf):
        if schema.validate(conf):
            for group in conf:
                if group.get("require_two_factor_authentication", False) is True:
                    return CheckResult.PASSED, conf
            return CheckResult.FAILED, conf


check = GroupsTwoFactorAuthentication()


```

### Running in CLI

```bash
#configure gitlab personal access token
export CI_JOB_TOKEN="ghp_abc"
#configure vpn (optional)
export REQUESTS_CA_BUNDLE="/usr/local/etc/openssl/cert.pem"
export BC_CA_BUNDLE="globalprotect_certifi.txt"

checkov -d . --framework gitlab_configuration
```

### Example output

```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: 2.0.722 


gitlab_configuration scan results:

Passed checks: 0, Failed checks: 1, Skipped checks: 0

Check: CKV_GITLAB_2: "Ensure all Gitlab groups require two factor authentication"
	FAILED for resource: /gitlab_conf/groups.json
	File: /gitlab_conf/groups.json:2-27

		2  |     {
		3  |         "id": 15483421,
		4  |         "web_url": "https://gitlab.com/groups/baraktest1",
		5  |         "name": "baraktestgroup",
		6  |         "path": "baraktest1",
		7  |         "description": "",
		8  |         "visibility": "private",
		9  |         "share_with_group_lock": false,
		10 |         "require_two_factor_authentication": false,
		11 |         "two_factor_grace_period": 48,
		12 |         "project_creation_level": "developer",
		13 |         "auto_devops_enabled": null,
		14 |         "subgroup_creation_level": "maintainer",
		15 |         "emails_disabled": null,
		16 |         "mentions_disabled": null,
		17 |         "lfs_enabled": true,
		18 |         "default_branch_protection": 2,
		19 |         "avatar_url": null,
		20 |         "request_access_enabled": true,
		21 |         "full_name": "baraktestgroup",
		22 |         "full_path": "baraktest1",
		23 |         "created_at": "2022-01-17T11:03:19.763Z",
		24 |         "parent_id": null,
		25 |         "ldap_cn": null,
		26 |         "ldap_access": null
		27 |     }



Process finished with exit code 1


```

To add more GitLab policies and configuration to be inspected take a look at the [GitLab policy contribution guide](https://www.checkov.io/6.Contribution/Contribute%20New%20Gitlab%20Policies.html)
