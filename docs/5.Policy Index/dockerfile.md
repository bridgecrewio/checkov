---
layout: default
title: dockerfile resource scans
nav_order: 1
---

# dockerfile resource scans (auto generated)

|    | Id           | Type       | Entity   | Policy                                                                   | IaC        |
|----|--------------|------------|----------|--------------------------------------------------------------------------|------------|
|  0 | CKV_DOCKER_1 | dockerfile | EXPOSE   | Ensure port 22 is not exposed                                            | dockerfile |
|  1 | CKV_DOCKER_2 | dockerfile | *        | Ensure that HEALTHCHECK instructions have been added to container images | dockerfile |
|  2 | CKV_DOCKER_3 | dockerfile | *        | Ensure that a user for the container has been created                    | dockerfile |
|  3 | CKV_DOCKER_4 | dockerfile | ADD      | Ensure that COPY is used instead of ADD in Dockerfiles                   | dockerfile |
|  4 | CKV_DOCKER_5 | dockerfile | RUN      | Ensure update instructions are not use alone in the Dockerfile           | dockerfile |


---


