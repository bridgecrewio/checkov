---
layout: default
published: true
title: CSV
nav_order: 20
---

# CSV

A CSV output would generate 3 output files:
- iac.csv
- container_images.csv
- oss_packages.csv

## Structure
###iac.csv
| Resource                 | Path                      | Git Org       | Git Repository  | Misconfigurations  | Severity  |
|:-------------------------|:--------------------------|:--------------|:----------------|:-------------------|:----------|
| aws_db_instance.default  | /terraform/aws/db-app.tf  | bridgecrewio  | terragoat       | CKV_AWS_161        | MEDIUM    |

###oss_packages.csv
| Package  | Version  | Path                                            | Git Org       | Git Repository  | Vulnerability   | Severity  | Licenses  |
|:---------|:---------|:------------------------------------------------|:--------------|:----------------|:----------------|:----------|:----------|
| xmldom   | 0.5.0    | /packages/node/twistcli-test/package-lock.json  | bridgecrewio  | terragoat       | CVE-2021-32796  | MEDIUM    |

###container_images.csv
| Package  | Version  | Path                             | Git Org       | Git Repository  | Vulnerability   | Severity  | Licenses  |
|:---------|:---------|:---------------------------------|:--------------|:----------------|:----------------|:----------|:----------|
| xmldom   | 0.5.0    | /Dockerfile  (sha256:6a353e22ce) | bridgecrewio  | terragoat       | CVE-2021-32796  | MEDIUM    |