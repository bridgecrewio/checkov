---
layout: default
title: dockerfile resource scans
nav_order: 1
---

# dockerfile resource scans (auto generated)

|    |               | Id         | Type       | Entity                                                                   | Policy     | IaC                                                                                                 |
|----|---------------|------------|------------|--------------------------------------------------------------------------|------------|-----------------------------------------------------------------------------------------------------|
|  0 | CKV_DOCKER_1  | dockerfile | EXPOSE     | Ensure port 22 is not exposed                                            | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/ExposePort22.py       |
|  1 | CKV_DOCKER_2  | dockerfile | *          | Ensure that HEALTHCHECK instructions have been added to container images | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/HealthcheckExists.py  |
|  2 | CKV_DOCKER_3  | dockerfile | *          | Ensure that a user for the container has been created                    | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/UserExists.py         |
|  3 | CKV_DOCKER_4  | dockerfile | ADD        | Ensure that COPY is used instead of ADD in Dockerfiles                   | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/AddExists.py          |
|  4 | CKV_DOCKER_5  | dockerfile | RUN        | Ensure update instructions are not use alone in the Dockerfile           | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/UpdateNotAlone.py     |
|  5 | CKV_DOCKER_6  | dockerfile | MAINTAINER | Ensure that LABEL maintainer is used instead of MAINTAINER (deprecated)  | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/MaintainerExists.py   |
|  6 | CKV_DOCKER_7  | dockerfile | FROM       | Ensure the base image uses a non latest version tag                      | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/ReferenceLatestTag.py |
|  7 | CKV_DOCKER_8  | dockerfile | USER       | Ensure the last USER is not root                                         | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/RootUser.py           |
|  8 | CKV_DOCKER_9  | dockerfile | RUN        | Ensure that APT isn't used                                               | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/RunUsingAPT.py        |
|  9 | CKV_DOCKER_10 | dockerfile | WORKDIR    | Ensure that WORKDIR values are absolute paths                            | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/WorkdirIsAbsolute.py  |
| 10 | CKV_DOCKER_11 | dockerfile | FROM       | Ensure From Alias are unique for multistage builds.                      | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/dockerfile/checks/AliasIsUnique.py      |
| 11 | CKV2_DOCKER_1 | resource   | RUN        | Ensure that sudo isn't used                                              | dockerfile | https://github.com/bridgecrewio/checkov/tree/master/checkov/common/graph/checks_infra/base_check.py |


---


