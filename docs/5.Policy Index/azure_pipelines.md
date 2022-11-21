---
layout: default
title: azure_pipelines resource scans
nav_order: 1
---

# azure_pipelines resource scans (auto generated)

|    |                      | Id              | Type                    | Entity                                             | Policy          | IaC                                                         |
|----|----------------------|-----------------|-------------------------|----------------------------------------------------|-----------------|-------------------------------------------------------------|
|  0 | CKV_AZUREPIPELINES_1 | azure_pipelines | jobs                    | Ensure container job uses a non latest version tag | Azure Pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  1 | CKV_AZUREPIPELINES_1 | azure_pipelines | stages[].jobs[]         | Ensure container job uses a non latest version tag | Azure Pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  2 | CKV_AZUREPIPELINES_2 | azure_pipelines | jobs                    | Ensure container job uses a version digest         | Azure Pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  3 | CKV_AZUREPIPELINES_2 | azure_pipelines | stages[].jobs[]         | Ensure container job uses a version digest         | Azure Pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  4 | CKV_AZUREPIPELINES_3 | azure_pipelines | jobs[].steps[]          | Ensure set variable is not marked as a secret      | Azure Pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  5 | CKV_AZUREPIPELINES_3 | azure_pipelines | stages[].jobs[].steps[] | Ensure set variable is not marked as a secret      | Azure Pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |


---


