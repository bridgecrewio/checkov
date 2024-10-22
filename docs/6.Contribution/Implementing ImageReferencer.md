# Implementing ImageReferencer
The relevant class can be found at `checkov/common/images/image_referencer.py`
## How was the idea born?
Container images are referenced widely across CI workflow files, Terraform, Serverless, K8 manifests, etc. 
Those files can naturally have a misconfig and reference an image with a vulnerability.

When using checkov with API token, checkov gets that capability to perform image scanning and utilize Prisma cloud compute vulnerability DB.
If `ImageReferencer` is derived by a `Runner`than referenced images in an IaC file can be scanned for vulnerabilities.

## Would container images are scanned automatically? 
Yes, If the `--framework` `sca_image` is not excluded from the execution scope, an API token is provided.
The automatic scanning is happening thanks to the registration process for any Derived class of ImageReferencers that occurs in `RunnerRegistry` init.    
Implementing image referencer will mean scan results will take additional time since images are being pulled.
 
## What needs to be implemented? 
Look at: `checkov/common/images/image_referencer.py`  
and the derived class: `checkov/github_actions/runner.py`


## Example CLI command 
```bash
checkov -d /checkov/integration_tests/example_workflow_file/.github/workflows/ --framework sca_image --bc-api-key SOME_TOKEN
```

```bash

       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x

github_actions scan results:

Passed checks: 7, Failed checks: 1, Skipped checks: 0

Check: CKV_GHA_1: "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn't true on environment variables on a job"
	PASSED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.my_job.CKV_GHA_1
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:8-17
Check: CKV_GHA_1: "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn't true on environment variables on a job"
	PASSED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.my_job2.CKV_GHA_1
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:18-27
Check: CKV_GHA_1: "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn't true on environment variables on a job"
	PASSED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.unsecure-job.CKV_GHA_1
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:28-36
Check: CKV_GHA_1: "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn't true on environment variables on a job"
	PASSED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.secure-job.CKV_GHA_1
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:37-40
Check: CKV_GHA_2: "Ensure run commands are not vulnerable to shell injection"
	PASSED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.my_job.CKV_GHA_2
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:8-17
Check: CKV_GHA_2: "Ensure run commands are not vulnerable to shell injection"
	PASSED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.my_job2.CKV_GHA_2
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:18-27
Check: CKV_GHA_2: "Ensure run commands are not vulnerable to shell injection"
	PASSED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.secure-job.CKV_GHA_2
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:37-40
Check: CKV_GHA_2: "Ensure run commands are not vulnerable to shell injection"
	FAILED for resource: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml.jobs.unsecure-job.CKV_GHA_2
	File: /Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml:28-36

		28 |     runs-on: ubuntu-latest
		29 |     run: |
		30 |       title="${{ github.event.issue.title }}"
		31 |       if [[ ! $title =~ ^.*:\ .*$ ]]; then
		32 |         echo "Bad issue title"
		33 |         exit 1
		34 |       fi
		35 |   secure-job:
		36 |     name: job2

sca_image scan results:

Passed checks: 0, Failed checks: 989, Skipped checks: 0

	//Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml (sha256:6a353e22ce)
	┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐
	│ Total CVEs: 344    │ critical: 8        │ high: 19           │ medium: 24         │ low: 293           │ skipped: 0         │
	├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤
	├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤
	│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │
	├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤
	│ libwebp            │ CVE-2018-25014     │ critical           │ 0.5.2-1            │ 0.5.2.post1+deb9u1 │ 0.5.2.post1+deb9u1 │
	│                    │ CVE-2018-25011     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25013     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25012     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25010     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25009     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36332     │ low                │                    │ N/A                │                    │
	│                    │ CVE-2020-36331     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36330     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36329     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36328     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤
	│ elfutils           │ CVE-2018-16402     │ critical           │ 0.168-1            │ 0.168.post1+deb9u1 │ 0.168.post1+deb9u1 │
	│                    │ CVE-2018-18520     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-18521     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-18310     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-16062     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-16403     │ low                │                    │ N/A                │                    │
	│                    │ CVE-2019-7665      │ low                │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2019-7150      │ low                │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2019-7149      │ low                │                    │ N/A                │                    │
	├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤

.... 
sca_image scan results:

Passed checks: 0, Failed checks: 989, Skipped checks: 0

	//Users/barak/Documents/dev/bridgecrew/checkov3/integration_tests/example_workflow_file/.github/workflows/vulnerable_container.yaml (sha256:6a353e22ce)
	┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐
	│ Total CVEs: 344    │ critical: 8        │ high: 19           │ medium: 24         │ low: 293           │ skipped: 0         │
	├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤
	├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤
	│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │
	├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤
	│ libwebp            │ CVE-2018-25014     │ critical           │ 0.5.2-1            │ 0.5.2.post1+deb9u1 │ 0.5.2.post1+deb9u1 │
	│                    │ CVE-2018-25011     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25013     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25012     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25010     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2018-25009     │ critical           │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36332     │ low                │                    │ N/A                │                    │
	│                    │ CVE-2020-36331     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36330     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36329     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	│                    │ CVE-2020-36328     │ low                │                    │ 0.5.2.post1+deb9u1 │                    │
	├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤
	│ elfutils           │ CVE-2018-16402     │ critical           │ 0.168-1            │ 0.168.post1+deb9u1 │ 0.168.post1+deb9u1 │
	│                    │ CVE-2018-18520     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-18521     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-18310     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-16062     │ medium             │                    │ 0.168.post1+deb9u1 │                    │
	│                    │ CVE-2018-16403     │ low                │                    │ N/A                │                    │
	│                    │ CVE-2019-7665      │ low                │                    │ 0.168.post1+deb9u1 │                    │
...
More details: https://www.bridgecrew.cloud/projects?repository=acme_cli_repo/workflows&branch=bc-a57cd90_master&runId=latest

```

## What would be a good candidate?
Serverless functions utilizing containers, and every other IaC manifest that can reference an image  
