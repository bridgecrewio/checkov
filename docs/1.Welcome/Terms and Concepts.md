---
layout: default
published: true
title: Terms and Concepts
nav_order: 2
---

# Terms and Concepts

**Policy:** Security policies define various aspects of your cloud configuration that impact the overall security of the environment. For example, multi-factor authentication should be enabled for the root account. A resource that is not in the state defined in a policy is non-compliant and will appear in scan results.

**Composite Policy:** A composite, or connection-state is one in which Checkov looks for resources, or types of resources that are or are not connected to other resources. For example, it may be essential for certain resource types to be connected to security groups; or it may be important that certain resource types are not connected to other resources with public access. On each scan, Checkov creates a virtual connection graph based on Composite Policies. Learn more about [creating composite policies in YAML format](https://www.checkov.io/3.Custom%20Policies/YAML%20Custom%20Policies.html).

**Incident:** Upon each scan, Checkov creates Incidents for each case of non-conformance to a Policy.

**Resource:** A Resource is a Cloud Platform entity, for example, an Amazon EC2 instance, a CloudFormation stack, or an Amazon S3 bucket.

**Suppression:** This is an action that can be taken to indicate that an Incident reported by Checkov is not problematic. When Suppressing an Incident, you can Suppress it for all relevant Resources or only specific Resources.

## Commonly used terms

**Infrastructure as code** frameworks are systems for automating infrastructure deployment, scaling and management using machine-readable configuration files.

**Declarative** configurations are absolute methods to design the execution of well-defined infrastructure building blocks.

**Imperative** configurations are procedural methods to design the steps required to build a required end-result.

**Immutable infrastructure** defines a version-controlled data model that enables reproducing point-in-time changes to individual attributes of a configuration manifest.

**Terraform** is a popular open source declarative infrastructure as code framework used primarily to define resource in public cloud services.

**CloudFormation** is a declarative infrastructure as code framework used to define resources in Amazon Web Services.

**Kubernetes** is a popular open source declarative infrastructure as code framework used primarily to orchestrate containers in a virtual computing environment.
