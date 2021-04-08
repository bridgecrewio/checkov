---
layout: default
published: true
title: Feature Descriptions
order: 4
---

# Feature Descriptions

With Checkov you can:

* Run a variety of scan types
* Enable Checkov to run as part of your CI/CD workflow
* Create and contribute custom Checkov policies

## Running Checkov

With Checkov you can scan a repository, branch, folder, or a single file with attribute-based misconfigurations or connection state errors. See [CLI Command Reference](../2.Basics/CLI%20Command%20Reference.md).

When running Checkov, you can also:

* [Review scan results](../2.Basics/Reviewing%20Scan%20Results.md)
* [Suppress or skip](../2.Basics/Suppressing%20and%20Skipping%20Policies.md)
* [Scan credentials and secrets](../2.Basics/Scanning%20Credentials%20and%20Secrets.md)
* [Scan Kubernetes clusters](../4.Integrations/Kubernetes.md)
* [Scan Terraform plan output and 3rd party modules](../4.Integrations/Terraform%20Scanning.md)

## Integrating with CI/CD
In addition to integrating with your code repository, Checkov can also integrate with your automated build pipeline via CI/CD providers. When your build tests run, Checkov will scan your infrastructure as code files for misconfigurations and you can review the output directly in your CI pipeline.

* [Integrate with Jenkins](../4.Integrations/Jenkins.md)
* [Integrate with Bitbucket Cloud Pipelines](../4.Integrations/Bitbucket%20Cloud%20Pipelines.md)
* [Integrate with Github Actions](../4.Integrations/GitHub%20Actions.md)
* [Integrate with Gitlab CLI](../4.Integrations/GitLab%20CLI.md)

## Custom Policies

* [Create custom Python attribute policies](../3.Custom%20Policies/Create%20Python%20Policies.md)
* [Create custom YAML attribute and composite policies](../3.Custom%20Policies/Create%20YAML%20Policies.md)
* [Custom policy examples](../3.Custom%20Policies/Examples.md)
* [Share custom policies across repos](../3.Custom%20Policies/Sharing%20Custom%20Policies.md)
