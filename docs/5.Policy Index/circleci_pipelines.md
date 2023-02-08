---
layout: default
title: circleci_pipelines resource scans
nav_order: 1
---

# circleci_pipelines resource scans (auto generated)

|    | Id                      | Type               | Entity                                                                                     | Policy                                                                      | IaC                | Resource Link                                                                                                                                  |
|----|-------------------------|--------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | CKV_CIRCLECIPIPELINES_1 | circleci_pipelines | jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}      | Ensure the pipeline image uses a non latest version tag                     | circleci_pipelines | [latest_image.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/latest_image.py)                         |
|  1 | CKV_CIRCLECIPIPELINES_2 | circleci_pipelines | jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}      | Ensure the pipeline image version is referenced via hash not arbitrary tag. | circleci_pipelines | [image_version_not_hash.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/image_version_not_hash.py)     |
|  2 | CKV_CIRCLECIPIPELINES_3 | circleci_pipelines | orbs.{orbs: @}                                                                             | Ensure mutable development orbs are not used.                               | circleci_pipelines | [prevent_development_orbs.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/prevent_development_orbs.py) |
|  3 | CKV_CIRCLECIPIPELINES_4 | circleci_pipelines | orbs.{orbs: @}                                                                             | Ensure unversioned volatile orbs are not used.                              | circleci_pipelines | [prevent_volatile_orbs.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/prevent_volatile_orbs.py)       |
|  4 | CKV_CIRCLECIPIPELINES_5 | circleci_pipelines | jobs.*.steps[]                                                                             | Suspicious use of netcat with IP address                                    | circleci_pipelines | [ReverseShellNetcat.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/ReverseShellNetcat.py)             |
|  5 | CKV_CIRCLECIPIPELINES_6 | circleci_pipelines | jobs.*.steps[]                                                                             | Ensure run commands are not vulnerable to shell injection                   | circleci_pipelines | [ShellInjection.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/ShellInjection.py)                     |
|  6 | CKV_CIRCLECIPIPELINES_7 | circleci_pipelines | jobs.*.steps[]                                                                             | Suspicious use of curl in run task                                          | circleci_pipelines | [SuspectCurlInScript.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/SuspectCurlInScript.py)           |
|  7 | CKV_CIRCLECIPIPELINES_8 | circleci_pipelines | executors.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__} | Detecting image usages in circleci pipelines                                | circleci_pipelines | [DetectImagesUsage.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/DetectImagesUsage.py)               |
|  8 | CKV_CIRCLECIPIPELINES_8 | circleci_pipelines | jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}      | Detecting image usages in circleci pipelines                                | circleci_pipelines | [DetectImagesUsage.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/circleci_pipelines/checks/DetectImagesUsage.py)               |


---


