---
layout: default
published: true
title: What is Checkov?
order: 1
---
Checkov is a static code analysis tool for scanning IaC files for misconfigurations that could lead to security problems. Checkov includes more than 750 predefined Policies to check for common misconfiguration issues and also supports creation and contribution of of Custom Policies.

## Supported IaC types

Checkov scans these IaC file types:

* Terraform (for AWS, GCP and Azure)
* CloudFormation
* ARM
* Kubernetes
* Docker

## Custom policies

Custom policies can be created to check cloud resources based on configuration attributes (in Python or YAML and check resource composite or connection-states (in YAML). In effect, Checkov creates a cloud resource connection graph for deep misconfiguration analysis. See [Create Custom Policy - - Attribute Check and Composite](doc:create-custom-policy-yaml-attribute-check-and-composite) to learn more about custom policies.

## Compliance with Industry Standards

In addition, Checkov scans check for compliance with common industry standards such as the Center for Internet Security (CIS) and Amazon Web Services (AWS) Foundations Benchmark.
