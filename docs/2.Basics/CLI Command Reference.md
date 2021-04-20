---
layout: default
published: true
title: CLI Command Reference
nav_order: 2
---

# CLI Command Reference

| Parameter | Description |
| --- | --- |
| `-h`, `--help` | Show this help message and exit. |
| `-v`, `--version` | Version. |
| `-d DIRECTORY`, `--directory DIRECTORY` | IaC root directory. Cannot be used together with --file. |
| `-f FILE`, `--file FILE` | IaC file. Cannot be used together with `--directory`. |
| `--external-checks-dir EXTERNAL_CHECKS_DIR` | Directory for custom checks to be loaded. Can be repeated. |
| `-l`, `--list` | List checks. |
| `-o [{cli,json,junitxml,github_failed_only}]`, `--output [{cli,json,junitxml,github_failed_only}]` | Report output format. |
| `--quiet` | Display only failed checks in CLI output. | [View Scan Results](doc:scan-use-cases#section-view-scan-results) |
| `--compact` | Do not display code blocks in CLI output. |
| `--framework {cloudformation,terraform,kubernetes,all}` | Filter scan to run only on a specific infrastructure code frameworks. Possible arguments are `cloudformation`, `terraform`, `kubernetes`, `all` |
| `-c CHECK`, `--check CHECK` | Filter scan to run only on a specific check identifier (allowlist). You can specify multiple checks separated by comma delimiter. |
| `--skip-check SKIP_CHECK` | Filter scan to run on all checks except for a specific check identifier (denylist). You can specify multiple checks separated by comma delimiter. | [Suppress or Skip](doc:scan-use-cases#section-suppress-or-skip) |
| `-s`, `--soft-fail` | Runs checks but suppresses error code. |
| `--bc-api-key BC_API_KEY` | Bridgecrew API key. |
| `--repo-id REPO_ID` | The identity string of the repository. It should be in the form: `<repo_owner>/<repo_name>` |
| `-b BRANCH`, `--branch BRANCH` | The selected branch of the persisted repository. Only has effect when using the `--bc-api-key` flag. |
| `-ca CA_CERTIFICATE`, `--ca-certificate CA_CERTIFICATE` | Custom CA (bundle) file. |
