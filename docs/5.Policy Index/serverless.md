---
layout: default
title: serverless resource scans
nav_order: 1
---

# serverless resource scans (auto generated)

|    | Id           | Type     | Entity   | Policy                                                                   | IaC        |
|----|--------------|----------|----------|--------------------------------------------------------------------------|------------|
|  0 | CKV_DOCKER_1 | resource | EXPOSE   | Ensure port 22 is not exposed                                            | serverless |
|  1 | CKV_DOCKER_2 | resource | *        | Ensure that HEALTHCHECK instructions have been added to container images | serverless |
|  2 | CKV_DOCKER_3 | resource | *        | Ensure that a user for the container has been created                    | serverless |
|  3 | CKV_DOCKER_4 | resource | ADD      | Ensure that COPY is used instead of ADD in Dockerfiles                   | serverless |
|  4 | CKV_DOCKER_5 | resource | RUN      | Ensure update instructions are not use alone in the Dockerfile           | serverless |


---


