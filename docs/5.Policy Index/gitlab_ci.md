---
layout: default
title: gitlab_ci resource scans
nav_order: 1
---

# gitlab_ci resource scans (auto generated)

|    |                | Id   | Type         | Entity                                                         | Policy    | IaC                                                         |
|----|----------------|------|--------------|----------------------------------------------------------------|-----------|-------------------------------------------------------------|
|  0 | CKV_GITLABCI_1 | jobs | *.script[]   | Suspicious use of curl with CI environment variables in script | gitlab_ci | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  1 | CKV_GITLABCI_2 | jobs | *.rules      | Avoid creating rules that generate double pipelines            | gitlab_ci | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  2 | CKV_GITLABCI_3 | jobs | *.image[]    | Detecting image usages in gitlab workflows                     | gitlab_ci | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  3 | CKV_GITLABCI_3 | jobs | *.services[] | Detecting image usages in gitlab workflows                     | gitlab_ci | https://github.com/bridgecrewio/checkov/tree/master/checkov |


---


