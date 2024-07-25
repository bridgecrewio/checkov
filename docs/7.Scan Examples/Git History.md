---
layout: default
published: false
title: Git History
nav_order: 20
---

# Git History
Checkov supports scanning of secrets in git history to identify and flag secrets, that might not be in the head commit of the branch but are still visible by accessing the git history of the repo.
Checkov fetches all the available commits and uses same scan as the Checkov 'secrets' checkov framework to search for secrets in the diff available from git history.
Each secret found can be traced to the first commit in which it appeared and the last commit that contained the secret if it was removed.


## Git History scanning

Git history scan uses the same signatures and models as a regular secrets scan.
The only difference is that the root directory is the path to either the root git directory or the bare git repo.
Using the `--scan-secrets-history` flag will scan git history for secrets only. This will not scan for other issues such as IaC misconfiguration. 
Use `--secrets-history-timeout` to set how long the secrets scan will run on history before stopping. If the timeout was not enough to finish the run, no results will be returned.  The default is `12h`.

A run with a timeout of `12h` by default:
```bash
checkov -d <git dir> --scan-secrets-history --bc-api-key <your_api_key> --repo-id <repo/name>
```

A run with a timeout of `1h`:
```bash
checkov -d <git dir> --scan-secrets-history --secrets-history-timeout 1h --bc-api-key <your_api_key> --repo-id <repo/name>
```

### Example output
on https://github.com/bridgecrewio/detect-secrets repo:
```bash
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: 2.3.172 


secrets scan results:

Passed checks: 0, Failed checks: 320, Skipped checks: 0

Check: CKV_SECRET_6: "Base64 High Entropy String"
	FAILED for resource: 732a8470a9623e89355d477688afd7f8f4d55e03
	Severity: LOW
	File: /tests/plugins/azure_storage_key_test.py:12-13; Commit Added: 018c9d1ee2a152a82c612ee82c0cd952a4f3eae4
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/secrets-policies/secrets-policy-index/git-secrets-6

		12 | 'Accoun*********************************************************************************************',  # noqa: E501

Check: CKV_SECRET_6: "Base64 High Entropy String"
	FAILED for resource: b57a3ad258d7674d2005a53aaa67460e25791f71
	Severity: LOW
	File: /tests/plugins/keyword_test.py:22-23; Commit Added: 01cde918f5f471cb0e03964db37f905e5bcdd1cf; Commit Removed: e01d818ad118b0b1fccb1cc9b406e7aa1539e242
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/secrets-policies/secrets-policy-index/git-secrets-6

		22 | 'PASSWORD = "ve********"'

Check: CKV_SECRET_2: "AWS Access Key"
	FAILED for resource: d70eab08607a4d05faa2d0d6647206599e9abc65
	Severity: LOW
	File: /test_diff/test_data/add_sample.diff:10-11; Commit Added: 07d52374f6d1ccc8709069be43139a6ba7ae544b
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/secrets-policies/secrets-policy-index/git-secrets-2
	
...

```