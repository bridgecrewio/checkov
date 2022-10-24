---
layout: default
title: dockerfile resource scans
nav_order: 1
---

# dockerfile resource scans (auto generated)

|    | Id            | Type       | Entity     | Policy                                                                   | IaC        |
|----|---------------|------------|------------|--------------------------------------------------------------------------|------------|
|  0 | CKV_DOCKER_1  | dockerfile | EXPOSE     | Ensure port 22 is not exposed                                            | dockerfile |
|  1 | CKV_DOCKER_2  | dockerfile | *          | Ensure that HEALTHCHECK instructions have been added to container images | dockerfile |
|  2 | CKV_DOCKER_3  | dockerfile | *          | Ensure that a user for the container has been created                    | dockerfile |
|  3 | CKV_DOCKER_4  | dockerfile | ADD        | Ensure that COPY is used instead of ADD in Dockerfiles                   | dockerfile |
|  4 | CKV_DOCKER_5  | dockerfile | RUN        | Ensure update instructions are not use alone in the Dockerfile           | dockerfile |
|  5 | CKV_DOCKER_6  | dockerfile | MAINTAINER | Ensure that LABEL maintainer is used instead of MAINTAINER (deprecated)  | dockerfile |
|  6 | CKV_DOCKER_7  | dockerfile | FROM       | Ensure the base image uses a non latest version tag                      | dockerfile |
|  7 | CKV_DOCKER_8  | dockerfile | USER       | Ensure the last USER is not root                                         | dockerfile |
|  8 | CKV_DOCKER_9  | dockerfile | RUN        | Ensure that APT isn't used                                               | dockerfile |
|  9 | CKV_DOCKER_10 | dockerfile | WORKDIR    | Ensure that WORKDIR values are absolute paths                            | dockerfile |
| 10 | CKV_DOCKER_11 | dockerfile | FROM       | Ensure From Alias are unique for multistage builds.                      | dockerfile |


---


