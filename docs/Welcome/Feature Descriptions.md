---
layout: default
published: true
title: Feature Descriptions
order: 4
---
With Checkov you can:

* Run a variety of scan types
* Enable Checkov to run as part of your CI/CD workflow
* Create and contribute custom Checkov policies

## Running Checkov

With Checkov you can scan a repository, branch, folder, or a single file with attribute-based misconfigurations or connection state errors. See [CLI Command Reference](../Basics/CLI%Command%Reference.md).

When running Checkov, you can also:

* [Review scan results](../Basics/Reviewing%Scan%Results.md)
* [Suppress or skip](../Basics/Suppressing%and%Skipping%Policies.md)
* [Scan credentials and secrets](../Basics/Scanning%Credentials%and%Secrets.md)
* [Scan Kubernetes clusters](../Integrations/Kubernetes.md)
* [Scan Terraform plan output and 3rd party modules](../Integrations/Terraform%Plans.md)

## Integrating with CI/CD
In addition to integrating with your code repository, Checkov can also integrate with your automated build pipeline via CI/CD providers. When your build tests run, Checkov will scan your infrastructure as code files for misconfigurations and you can review the output directly in your CI pipeline.

* [Integrate with Jenkins](doc:jenkins)
* [Integrate with Bitbucket Cloud Pipelines](doc:bitbucket-cloud-pipelines)
* [Integrate with Github Actions](doc:github-actions)
* [Integrate with Gitlab CLI](doc:gitlab-cli)

## Custom Policies

* [Create custom Python attribute policies](../Custom%Policies/Create%Python%Policies.md)
* [Create custom YAML attribute and composite policies](../Custom%Policies/Create%YAML%Policies.md)
* [Custom policy examples](../Custom%Policies/Examples.md)
* [Share custom policies across repos](../Custom%Policies/Sharing%Custom%Policies.md)

## Contribution
* [Contribute New Provider](../Contribution/Contribute%New%Provider.md)
* [Contribute New Policy](../Contribution/Contribute%New%Policy.md)
