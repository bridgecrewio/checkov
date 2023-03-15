---
layout: default
title: argo_workflows resource scans
nav_order: 1
---

# argo_workflows resource scans (auto generated)

|    | Id         | Type           | Entity   | Policy                                                        | IaC            | Resource Link                                                                                                                                 |
|----|------------|----------------|----------|---------------------------------------------------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | CKV_ARGO_1 | argo_workflows | spec     | Ensure Workflow pods are not using the default ServiceAccount | Argo Workflows | [DefaultServiceAccount.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/argo_workflows/checks/template/DefaultServiceAccount.py) |
|  1 | CKV_ARGO_2 | argo_workflows | spec     | Ensure Workflow pods are running as non-root user             | Argo Workflows | [RunAsNonRoot.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/argo_workflows/checks/template/RunAsNonRoot.py)                   |


---


