---
layout: default
title: bitbucket_pipelines resource scans
nav_order: 1
---

# bitbucket_pipelines resource scans (auto generated)

|    | Id                       | Type                | Entity                                                                                           | Policy                                                  | IaC                 | Resource Link                                                                                                           |
|----|--------------------------|---------------------|--------------------------------------------------------------------------------------------------|---------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------|
|  0 | CKV_BITBUCKETPIPELINES_1 | bitbucket_pipelines | [{image:image,__startline__:__startline__,__endline__:__endline__}]                              | Ensure the pipeline image uses a non latest version tag | bitbucket_pipelines | [latest_image.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/bitbucket_pipelines/checks/latest_image.py) |
|  1 | CKV_BITBUCKETPIPELINES_1 | bitbucket_pipelines | pipelines.*.[*][][][].step.{image: image, __startline__: __startline__, __endline__:__endline__} | Ensure the pipeline image uses a non latest version tag | bitbucket_pipelines | [latest_image.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/bitbucket_pipelines/checks/latest_image.py) |
|  2 | CKV_BITBUCKETPIPELINES_1 | bitbucket_pipelines | pipelines.default[].step.{image: image, __startline__: __startline__, __endline__:__endline__}   | Ensure the pipeline image uses a non latest version tag | bitbucket_pipelines | [latest_image.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/bitbucket_pipelines/checks/latest_image.py) |


---


