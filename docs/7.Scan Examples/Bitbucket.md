---
layout: default
published: true
title: Bitbucket configuration scanning
nav_order: 20
---

# Bitbucket configuration scanning
Checkov supports the evaluation of policies on your Bitbucket organization and repositories settings.
When using checkov with Bitbucket token it can collect your current org settings and validate it complies with Bitbucket security best practices such as having branch protection rules having 2 approvals.
Full list of bitbucket organization and repository settings related checks can be found [here](https://www.checkov.io/5.Policy%20Index/bitbucket_configuration.html).

## Bitbucket scanning configuration

| Environment Variable          | Default value     | Description    |
|-------------|----------|-------------------------------------------|
| CKV_BITBUCKET_CONFIG_FETCH_DATA| "True" | checkov will try to fetch Bitbucket configuration from API by default (unless no access token provided)  |
| CKV_BITBUCKET_CONF_DIR_NAME   | "bitbucket_conf" | checkov will create a new directory named "bitbucket_conf" under current working directory                          |
| CI_SERVER_URL   | "https://api.bitbucket.com/" |  |
| APP_PASSWORD   |  | Bitbucket personal access token to be used to fetch Bitbucket configuration |
| BITBUCKET_USERNAME |  | Bitbucket username (not email) |
| BITBUCKET_REPO_FULL_NAME |  | workspace/repository, for example prisma/terragoat |

### Example branch restrictions configuration

```json
{
  "pagelen": 10,
  "values": [
    {
      "kind": "require_default_reviewer_approvals_to_merge",
      "users": [],
      "links": {
        "self": {
          "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26522110"
        }
      },
      "pattern": "master",
      "value": 1,
      "branch_match_kind": "glob",
      "groups": [],
      "type": "branchrestriction",
      "id": 26522110
    },
    {
      "kind": "require_approvals_to_merge",
      "users": [],
      "links": {
        "self": {
          "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520791"
        }
      },
      "pattern": "master",
      "value": 3,
      "branch_match_kind": "glob",
      "groups": [],
      "type": "branchrestriction",
      "id": 26520791
    },
    {
      "kind": "force",
      "users": [],
      "links": {
        "self": {
          "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520790"
        }
      },
      "pattern": "master",
      "value": null,
      "branch_match_kind": "glob",
      "groups": [],
      "type": "branchrestriction",
      "id": 26520790
    },
    {
      "kind": "delete",
      "users": [],
      "links": {
        "self": {
          "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520789"
        }
      },
      "pattern": "master",
      "value": null,
      "branch_match_kind": "glob",
      "groups": [],
      "type": "branchrestriction",
      "id": 26520789
    }
  ],
  "page": 1,
  "size": 4
}
```

### Example policy

```python
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.bitbucket.base_bitbucket_configuration_check import BaseBitbucketCheck
from checkov.bitbucket.schemas.branch_restrictions import schema as branch_restrictions_schema
from checkov.json_doc.enums import BlockType


class MergeRequestRequiresApproval(BaseBitbucketCheck):
    def __init__(self):
        name = "Merge requests should require at least 2 approvals"
        id = "CKV_BITBUCKET_1"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf):
        if branch_restrictions_schema.validate(conf):
            for value in conf.get("values", []):
                if value.get('kind','') == 'require_approvals_to_merge':
                    if value.get('value',0)>=2:
                        return CheckResult.PASSED, conf
            return CheckResult.FAILED, conf


check = MergeRequestRequiresApproval()


```

### Running in CLI

```bash
#configure bitbucket personal access token
export APP_PASSWORD="ghp_abc"
export BITBUCKET_USERNAME="username"
export BITBUCKET_REPO_FULL_NAME="prisma/terragoat"

checkov -d . --framework bitbucket_configuration
```

### Example output

```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      


bitbucket_configuration scan results:

Passed checks: 0, Failed checks: 2, Skipped checks: 0

Check: CKV_BITBUCKET_1: "Merge requests should require at least 2 approvals"
	FAILED for resource: /bitbucket_conf/branch_restrictions.json
	File: /bitbucket_conf/branch_restrictions.json:2-66

		2  |     "pagelen": 10,
		3  |     "values": [
		4  |         {
		5  |             "kind": "require_default_reviewer_approvals_to_merge",
		6  |             "users": [],
		7  |             "links": {
		8  |                 "self": {
		9  |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26522110"
		10 |                 }
		11 |             },
		12 |             "pattern": "master",
		13 |             "value": 1,
		14 |             "branch_match_kind": "glob",
		15 |             "groups": [],
		16 |             "type": "branchrestriction",
		17 |             "id": 26522110
		18 |         },
		19 |         {
		20 |             "kind": "require_approvals_to_merge",
		21 |             "users": [],
		22 |             "links": {
		23 |                 "self": {
		24 |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520791"
		25 |                 }
		26 |             },
		27 |             "pattern": "master",
		28 |             "value": 1,
		29 |             "branch_match_kind": "glob",
		30 |             "groups": [],
		31 |             "type": "branchrestriction",
		32 |             "id": 26520791
		33 |         },
		34 |         {
		35 |             "kind": "force",
		36 |             "users": [],
		37 |             "links": {
		38 |                 "self": {
		39 |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520790"
		40 |                 }
		41 |             },
		42 |             "pattern": "master",
		43 |             "value": null,
		44 |             "branch_match_kind": "glob",
		45 |             "groups": [],
		46 |             "type": "branchrestriction",
		47 |             "id": 26520790
		48 |         },
		49 |         {
		50 |             "kind": "delete",
		51 |             "users": [],
		52 |             "links": {
		53 |                 "self": {
		54 |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520789"
		55 |                 }
		56 |             },
		57 |             "pattern": "master",
		58 |             "value": null,
		59 |             "branch_match_kind": "glob",
		60 |             "groups": [],
		61 |             "type": "branchrestriction",
		62 |             "id": 26520789
		63 |         }
		64 |     ],
		65 |     "page": 1,
		66 |     "size": 4


Check: CKV_BITBUCKET_1: "Merge requests should require at least 2 approvals"
	FAILED for resource: /bitbucket_conf/project_approvals.json
	File: /bitbucket_conf/project_approvals.json:2-66

		2  |     "pagelen": 10,
		3  |     "values": [
		4  |         {
		5  |             "kind": "require_default_reviewer_approvals_to_merge",
		6  |             "users": [],
		7  |             "links": {
		8  |                 "self": {
		9  |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26522110"
		10 |                 }
		11 |             },
		12 |             "pattern": "master",
		13 |             "value": 1,
		14 |             "branch_match_kind": "glob",
		15 |             "groups": [],
		16 |             "type": "branchrestriction",
		17 |             "id": 26522110
		18 |         },
		19 |         {
		20 |             "kind": "require_approvals_to_merge",
		21 |             "users": [],
		22 |             "links": {
		23 |                 "self": {
		24 |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520791"
		25 |                 }
		26 |             },
		27 |             "pattern": "master",
		28 |             "value": 1,
		29 |             "branch_match_kind": "glob",
		30 |             "groups": [],
		31 |             "type": "branchrestriction",
		32 |             "id": 26520791
		33 |         },
		34 |         {
		35 |             "kind": "force",
		36 |             "users": [],
		37 |             "links": {
		38 |                 "self": {
		39 |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520790"
		40 |                 }
		41 |             },
		42 |             "pattern": "master",
		43 |             "value": null,
		44 |             "branch_match_kind": "glob",
		45 |             "groups": [],
		46 |             "type": "branchrestriction",
		47 |             "id": 26520790
		48 |         },
		49 |         {
		50 |             "kind": "delete",
		51 |             "users": [],
		52 |             "links": {
		53 |                 "self": {
		54 |                     "href": "https://api.bitbucket.org/2.0/repositories/shaharsamira/terragoat2/branch-restrictions/26520789"
		55 |                 }
		56 |             },
		57 |             "pattern": "master",
		58 |             "value": null,
		59 |             "branch_match_kind": "glob",
		60 |             "groups": [],
		61 |             "type": "branchrestriction",
		62 |             "id": 26520789
		63 |         }
		64 |     ],
		65 |     "page": 1,
		66 |     "size": 4

```

To add more Bitbucket policies and configuration to be inspected take a look at the [Bitbucket policy contribution guide](https://www.checkov.io/6.Contribution/Contribute%20New%20Bitbucket%20Policies.html)
