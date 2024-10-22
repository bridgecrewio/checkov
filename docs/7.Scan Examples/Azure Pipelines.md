---
layout: default
published: true
title: Azure Pipelines configuration scanning
nav_order: 20
---

# Azure Pipelines configuration scanning
Checkov supports the evaluation of policies on your Azure Pipelines files.
When using checkov to scan a directory that contains Azure Pipelines templates it will validate if the file is compliant with Azure Pipelines best practices such as usage of digest for container image version and more.  

Full list of Azure Pipelines policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/azure_pipelines.html).

### Example misconfigured Azure Pipelines template

```yaml
trigger:
- master

resources:
  repositories:
  - repository: AzureDevOps
    type: git
    endpoint: AzureDevOps
    name: AzureDevOps/AzureDevOps

jobs:
- job: RunInContainer
  pool:
    vmImage: 'ubuntu-18.04'

  container: ubuntu:20.04

  steps:
    - script: printenv
```
### Running in CLI

```bash
checkov -d . --framework azure_pipelines
```

### Example output
```bash
 
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x


azure_pipelines scan results:

Passed checks: 1, Failed checks: 1, Skipped checks: 0

Check: CKV_AZUREPIPELINES_1: "Ensure container job uses a non latest version tag"
	PASSED for resource: /azure-pipelines.yml.jobs.jobs.CKV_AZUREPIPELINES_1[12:20]
	File: /azure-pipelines.yml:12-21
Check: CKV_AZUREPIPELINES_2: "Ensure container job uses a version digest"
	FAILED for resource: /azure-pipelines.yml.jobs.jobs.CKV_AZUREPIPELINES_2[12:20]
	File: /azure-pipelines.yml:12-21

		12 | - job: RunInContainer
		13 |   pool:
		14 |     vmImage: 'ubuntu-18.04'
		15 | 
		16 |   container: ubuntu:20.04
		17 | 
		18 |   steps:
		19 |     - script: printenv
```
