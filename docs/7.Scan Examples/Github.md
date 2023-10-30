---
layout: default
published: true
title: GitHub configuration scanning
nav_order: 20
---

# GitHub configuration scanning
Checkov supports the evaluation of policies on your GitHub organization and repositories settings.
When using checkov with GitHub token it can collect your current org settings and validate it complies with GitHub security best practices such as having 2FA defined, having SSO and more.
Full list of github organization and repository settings related checks can be found [here](https://www.checkov.io/5.Policy%20Index/github_configuration.html).

## GitHub scanning configuration

| Environment Variable          | Default value             | Description                                                                                                                                   |
|-------------|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| CKV_GITHUB_CONFIG_FETCH_DATA| "True"                    | checkov will try to fetch GitHub configuration from API by default (unless no access token provided)                                          |
| CKV_GITHUB_CONF_DIR_NAME   | "github_conf"             | checkov will create a new directory named "github_conf" under current working directory                                                       |
| GITHUB_API_URL   | "https://api.github.com/" |                                                                                                                                               |
| GITHUB_TOKEN   |                           | GitHub personal access token to be used to fetch GitHub configuration                                                                         |
| GITHUB_REF | refs/heads/master                    | Github branch for which to fetch branch protection rules configuration                                                                        |
 | GITHUB_ORG   |                           | Github organization                                                                                                                           |
 | GITHUB_REPOSITORY |                      | Github repositry for which to fetch repository configuration info                                                                             |
 | GITHUB_REPO_OWNER |                           | The owner of the repository. This could be either Github repository owner user name or the organization name, in which the user is the owner. |

### Example organization security configuration

```json
{
    "data": {
        "organization": {
            "name": "Prisma",
            "login": "prismaio",
            "description": "Secure public cloud infrastructure",
            "ipAllowListEnabledSetting": "ENABLED",
            "ipAllowListForInstalledAppsEnabledSetting": "ENABLED",
            "requiresTwoFactorAuthentication": false,
            "samlIdentityProvider": {
                "ssoUrl": "https://prisma.okta.com/app/githubcloud/foo/sso/saml"
            }
        }
    }
}
```

### Example policy

```python
from checkov.github.base_github_org_security import OrgSecurity


class Github2FA(OrgSecurity):
    def __init__(self):
        name = "Ensure GitHub organization security settings require 2FA"
        id = "CKV_GITHUB_1"
        super().__init__(
            name=name,
            id=id
        )

    def get_evaluated_keys(self):
        return ['data/organization/requiresTwoFactorAuthentication']



check = Github2FA()

```

### Running in CLI

```bash
#configure github personal access token
export GITHUB_TOKEN="ghp_abc"
#configure vpn (optional)
export REQUESTS_CA_BUNDLE="/usr/local/etc/openssl/cert.pem"
export BC_CA_BUNDLE="globalprotect_certifi.txt"

checkov -d . --framework github_configuration
```

### Example output

```bash

       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: 2.0.707 

github_configuration scan results:

Passed checks: 2, Failed checks: 1, Skipped checks: 0

Check: CKV_GITHUB_3: "Ensure GitHub organization security settings has IP allow list enabled"
	PASSED for resource: _conf/org_security.json
	File: /github_conf/org_security.json:2-15

Check: CKV_GITHUB_2: "Ensure GitHub organization security settings require SSO"
	PASSED for resource: _conf/org_security.json
	File: /github_conf/org_security.json:2-15

Check: CKV_GITHUB_1: "Ensure GitHub organization security settings require 2FA"
	FAILED for resource: _conf/org_security.json
	File: /github_conf/org_security.json:2-15

		2  |     "data": {
		3  |         "organization": {
		4  |             "name": "Prisma",
		5  |             "login": "prismaio",
		6  |             "description": "Secure public cloud infrastructure",
		7  |             "ipAllowListEnabledSetting": "ENABLED",
		8  |             "ipAllowListForInstalledAppsEnabledSetting": "ENABLED",
		9  |             "requiresTwoFactorAuthentication": false,
		10 |             "samlIdentityProvider": {
		11 |                                 "ssoUrl": "https://prisma.okta.com/app/githubcloud/foo/sso/saml"
		12 |             }
		13 |         }
		14 |     }
		15 | }


```

To add more GitHub policies and configuration to be inspected take a look at the [GitHub policy contribution guide](https://www.checkov.io/6.Contribution/Contribute%20New%20GitHub%20Policies.html)
