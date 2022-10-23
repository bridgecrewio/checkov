---
layout: default
published: true
title: Feature Descriptions
nav_order: 4
---

# Feature Descriptions

With Checkov you can:

* Run a variety of scan types
* Enable Checkov to run as part of your CI/CD workflow
* Create and contribute custom Checkov policies

## Running Checkov

With Checkov you can scan a repository, branch, folder, or a single file with attribute-based misconfigurations or connection state errors. See [CLI Command Reference](https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html).

When running Checkov, you can also:

* [Review scan results](https://www.checkov.io/2.Basics/Reviewing%20Scan%20Results.html)
* [Suppress or skip](https://www.checkov.io/2.Basics/Suppressing%20and%20Skipping%20Policies.html)
* [Scan credentials and secrets](https://www.checkov.io/2.Basics/Scanning%20Credentials%20and%20Secrets.html)
* [Scan Kubernetes clusters](https://www.checkov.io/4.Integrations/Kubernetes.html)
* [Scan Terraform plan output and 3rd party modules](https://www.checkov.io/7.Scan%20Examples/Terraform%20Plan%20Scanning.html)

## Integrating with CI/CD
In addition to integrating with your code repository, Checkov can also integrate with your automated build pipeline via CI/CD providers. When your build tests run, Checkov will scan your infrastructure as code files for misconfigurations and you can review the output directly in your CI pipeline.

* [Integrate with Jenkins](https://www.checkov.io/4.Integrations/Jenkins.html)
* [Integrate with Bitbucket Cloud Pipelines](https://www.checkov.io/4.Integrations/Bitbucket%20Cloud%20Pipelines.html)
* [Integrate with Github Actions](https://www.checkov.io/4.Integrations/GitHub%20Actions.html)
* [Integrate with Gitlab CI](https://www.checkov.io/4.Integrations/GitLab%20CI.html)

## Custom Policies

* [Create custom Python attribute policies](https://www.checkov.io/3.Custom%20Policies/Python%20Custom%20Policies.html)
* [Create custom YAML attribute and composite policies](https://www.checkov.io/3.Custom%20Policies/YAML%20Custom%20Policies.html)
* [Custom policy examples](https://www.checkov.io/3.Custom%20Policies/Examples.html)
* [Share custom policies across repos](https://www.checkov.io/3.Custom%20Policies/Sharing%20Custom%20Policies.html)
