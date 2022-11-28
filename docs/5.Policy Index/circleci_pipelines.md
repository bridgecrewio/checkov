---
layout: default
title: circleci_pipelines resource scans
nav_order: 1
---

# circleci_pipelines resource scans (auto generated)

|    |                         | Id                 | Type                                                                                       | Entity                                                                      | Policy             | IaC                                                         |
|----|-------------------------|--------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------|-------------------------------------------------------------|
|  0 | CKV_CIRCLECIPIPELINES_1 | circleci_pipelines | jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}      | Ensure the pipeline image uses a non latest version tag                     | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  1 | CKV_CIRCLECIPIPELINES_2 | circleci_pipelines | jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}      | Ensure the pipeline image version is referenced via hash not arbitrary tag. | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  2 | CKV_CIRCLECIPIPELINES_3 | circleci_pipelines | orbs.{orbs: @}                                                                             | Ensure mutable development orbs are not used.                               | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  3 | CKV_CIRCLECIPIPELINES_4 | circleci_pipelines | orbs.{orbs: @}                                                                             | Ensure unversioned volatile orbs are not used.                              | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  4 | CKV_CIRCLECIPIPELINES_5 | circleci_pipelines | jobs.*.steps[]                                                                             | Suspicious use of netcat with IP address                                    | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  5 | CKV_CIRCLECIPIPELINES_6 | circleci_pipelines | jobs.*.steps[]                                                                             | Ensure run commands are not vulnerable to shell injection                   | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  6 | CKV_CIRCLECIPIPELINES_7 | circleci_pipelines | jobs.*.steps[]                                                                             | Suspicious use of curl in run task                                          | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |
|  7 | CKV_CIRCLECIPIPELINES_8 | circleci_pipelines | executors.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__} | Detecting image usages in circleci pipelines                                | circleci_pipelines | https://github.com/bridgecrewio/checkov/tree/master/checkov |


---


