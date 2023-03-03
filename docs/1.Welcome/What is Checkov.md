---
layout: default
published: true
title: What is Checkov?
nav_order: 1
---

# What is Checkov?

Checkov is a static code analysis tool for scanning infrastructure as code (IaC) files for misconfigurations that may lead to security or compliance problems. Checkov includes more than 750 predefined policies to check for common misconfiguration issues. Checkov also supports the creation and contribution of [custom policies](https://www.checkov.io/3.Custom%20Policies/Custom%20Policies%20Overview.html).

## Supported IaC types

Checkov scans these IaC file types:

* Terraform (for AWS, GCP, Azure and OCI)
* CloudFormation (including AWS SAM)
* Azure Resource Manager (ARM)
* Serverless framework
* Helm charts
* Kubernetes
* Docker

## Custom policies

Custom policies can be created to check cloud resources based on configuration attributes (in [Python](https://www.checkov.io/3.Custom%20Policies/Python%20Custom%20Policies.html) or [YAML](https://www.checkov.io/3.Custom%20Policies/YAML%20Custom%20Policies.html) or connection states (in [YAML](https://www.checkov.io/3.Custom%20Policies/YAML%20Custom%20Policies.html)). For composite policies, Checkov creates a cloud resource connection graph for deep misconfiguration analysis across resource relationships.

## Compliance with Industry Standards

In addition, Checkov scans for compliance with common industry standards such as the Center for Internet Security (CIS) and Amazon Web Services (AWS) Foundations Benchmark.

## Integrates seamlessly with Bridgecrew

Checkov integrates with advanced features in the [Bridgecrew platform](https://bridgecrew.io/platform). You can sign up for a free Bridgecrew account by running Checkov with no arguments and following the CLI prompts, or directly via the [Bridgecrew website](https://www.bridgecrew.cloud/login/signUp). Bridgecrew extends Checkov's capabilities to provide runtime scanning and visibility, native VCS integrations, compliance benchmarking, and more.

### Runtime Scanning

Bridgecrew can validate the same Checkov IaC policies against your runtime cloud environments in AWS, Azure and Google Cloud, allowing you to find and fix issues in existing deployments and detect cloud drifts. Read more in [Bridgecrew's documentation](https://docs.bridgecrew.io/docs/step-2-integrate-with-cloud-provider).


### Pull Request Annotations

Enable automated pull/merge request annotations on your repositories without having to build a CI pipeline or run scheduled checks. The Bridgecrew platform will automatically scan new pull requests and annotate them with comments for any policy violations discovered. Read more in [Bridgecrew's documentation](https://docs.bridgecrew.io/docs/step-3-integrate-with-code-repository).

![Pull Request](pull-request.png)

![Pull Request Annotations](pull-request-annotations.png)

### Repository Badges

Dynamic git repository badges to show compliance targets or currently failing policies. Read more in [Bridgecrew's documentation](https://docs.bridgecrew.io/docs/code-repository-badges).

![Readme Badges](readme-badges.png)

### Compliance Reports

Automate the creation of rich, detailed PDF reports for numerous compliance benchmarks, such as SOC2, HIPAA and PCI-DSS using the data within the Bridgecrew platform from your repositories and runtime environments.

![Sample PCI Report](sample-pci-report.png)
