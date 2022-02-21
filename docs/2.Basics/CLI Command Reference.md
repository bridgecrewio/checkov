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
| `--add-check` | Generate a new check via CLI prompt |
| `-f FILE`, `--file FILE` | IaC file. Cannot be used together with `--directory`. |
| `--skip-path SKIP_PATH` | Path (file or directory) to skip, using regular expression logic, relative to current working directory. Word boundaries are not implicit; i.e., specifying "dir1" will skip any directory or subdirectory named "dir1". Ignored with -f. Can be specified multiple times. |
| `--external-checks-dir EXTERNAL_CHECKS_DIR` | Directory for custom checks to be loaded. Can be repeated. |
| `--external-checks-git EXTERNAL_CHECKS_GIT` | Github url of external checks to be added. \n you can specify a subdirectory after a double-slash //. \n cannot be used together with --external-checks-dir' |
| `-l`, `--list` | List checks. |
| `-o {cli,cyclonedx,json,junitxml,github_failed_only,sarif}`, `--output {cli,cyclonedx,json,junitxml,github_failed_only,sarif}` | Report output format. Add multiple outputs by using the flag multiple times (`-o sarif -o cli`) |
| `--output-bc-ids` | Print Bridgecrew platform IDs (BC...) instead of Checkov IDs (CKV...), if the check exists in the platform |
| `--no-guide` | Do not fetch Bridgecrew platform IDs and guidelines for the checkov output report. Note: this prevents Bridgecrew platform check IDs from being used anywhere in the CLI. |
| `--quiet` | Display only failed checks in CLI output. | [View Scan Results](doc:scan-use-cases#section-view-scan-results) |
| `--compact` | Do not display code blocks in CLI output. |
| `--framework {cloudformation,terraform,kubernetes,serverless,arm,terraform_plan,helm,dockerfile,secrets,json,all}` | Filter scan to run only on a specific infrastructure code frameworks. Possible arguments are `cloudformation`, `terraform`, `kubernetes`, `serverless`, `arm`, `terraform_plan`, `helm`, `dockerfile`, `secrets`, `json`, `all` |
| `--skip-framework {cloudformation,terraform,kubernetes,serverless,arm,terraform_plan,helm,dockerfile,secrets,json}` | Filter scan to skip specific infrastructure code frameworks. will be included automatically for some frameworks if system dependencies are missing.
| `-c CHECK`, `--check CHECK` | Filter scan to run only on a specific check identifier (allowlist). You can specify multiple checks separated by comma delimiter. |
| `--skip-check SKIP_CHECK` | Filter scan to run on all checks except for a specific check identifier (denylist). You can specify multiple checks separated by comma delimiter. | [Suppress or Skip](doc:scan-use-cases#section-suppress-or-skip) |
| `--run-all-external-checks` | Run all external checks (loaded via --external-checks options) even if the checks are not present in the --check list. This allows you to always ensure that new checks present in the external source are used. If an external check is included in --skip-check, it will still be skipped. |
| `--bc-api-key BC_API_KEY` | Bridgecrew API key [env var: BC_API_KEY] | 
| `--docker-image DOCKER_IMAGE` | Scan docker images by name or ID. Only works with --bc-api-key flag | 
| `--dockerfile-path DOCKERFILE_PATH` | Path to the Dockerfile of the scanned docker image | 
| `--repo-id REPO_ID` | Identity string of the repository, with form <repo_owner>/<repo_name> | 
| `-b BRANCH`, `--branch BRANCH` | Selected branch of the persisted repository. Only has effect when using the --bc-api-key flag | 
| `--skip-fixes` | Do not download fixed resource templates from Bridgecrew. Only has effect when using the --bc-api-key flag | 
| `--skip-suppressions` | Do not download preconfigured suppressions from the Bridgecrew platform. Code comment suppressions will still be honored. Only has effect when using the --bc-api-key flag | 
| `--skip-policy-download` | Do not download custom policies configured in the Bridgecrew platform. Only has effect when using the --bc-api-key flag | 
| `--download-external-modules DOWNLOAD_EXTERNAL_MODULES` | download external terraform modules from public git repositories and terraform registry [env var: DOWNLOAD_EXTERNAL_MODULES] | 
| `--var-file VAR_FILE` | Variable files to load in addition to the default files (see https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files).Currently only supported for source Terraform (.tf file), and Helm chart scans.Requires using --directory, not --file. | 
| `--external-modules-download-path EXTERNAL_MODULES_DOWNLOAD_PATH` | set the path for the download external terraform modules [env var: EXTERNAL_MODULES_DIR] | 
| `--evaluate-variables EVALUATE_VARIABLES` | evaluate the values of variables and locals | 
| `-ca CA_CERTIFICATE`, `--ca-certificate CA_CERTIFICATE` | Custom CA certificate (bundle) file [env var: BC_CA_BUNDLE] |
| `--repo-root-for-plan-enrichment REPO_ROOT_FOR_PLAN_ENRICHMENT` | Directory containing the hcl code used to generate a given plan file. Use with -f. | 
| `--config-file CONFIG_FILE` | path to the Checkov configuration YAML file | 
| `--create-config CREATE_CONFIG` | takes the current command line args and writes them out to a config file at the given path
| `--show-config` | prints all args and config settings and where they came from (eg. commandline, config file, environment variable or default)
| `--create-baseline` | Alongside outputting the findings, save all results to .checkov.baseline file so future runs will not re-flag the same noise. Works only with `--directory` flag | 
| `--baseline BASELINE` | Use a .checkov.baseline file to compare current results with a known baseline. Report will include only failed checks that are new with respect to the provided baseline | 
| `-s`, `--soft-fail` | Runs checks but suppresses error code | 
| `--soft-fail-on SOFT_FAIL_ON` | Exits with a 0 exit code for specified checks. You can specify multiple checks separated by comma delimiter | 
| `--hard-fail-on HARD_FAIL_ON` | Exits with a non-zero exit code for specified checks. You can specify multiple checks separated by comma delimiter | 
