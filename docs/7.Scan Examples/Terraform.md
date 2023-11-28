---
layout: default
published: true
title: Terraform Scanning
nav_order: 8
---

# Terraform Scanning

## Scanning Third-Party Terraform Modules

Third-party Terraform modules often reduce complexity for deploying services made up of many objects.

For example, the official AWS EKS module reduces the amount of configuration required to just few lines below.
However, in doing so abstracts the Terraform configuration away from a regular Checkov scan on the current directory.

```hcl
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "my-cluster"
  cluster_version = "1.24"
  subnets         = ["subnet-abcde012", "subnet-bcde012a", "subnet-fghi345a"]
  vpc_id          = "vpc-1234556abcdef"

  worker_groups = [
    {
      instance_type = "m4.large"
      asg_max_size  = 5
    }
  ]
}
```

To ensure coverage of objects within these modules, you can instruct Checkov to download those external modules:

```shell
checkov -d . --download-external-modules true
```

This will allow Checkov to download any external modules referenced in the Terraform configuration files into a folder named `.external_modules`.
To adjust the download path you can leverage the flag `--external-modules-download-path`:

```shell
checkov -d . --download-external-modules true --external-modules-download-path example/path
```

> [!NOTE]
> **Experimental**
> By setting the env var `CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES=True` instead of downloading external modules `checkov` will use the ones already downloaded by Terraform stored in `.terraform` folder. This only works for scans of the root folder, where also `terraform init` was executed.
> ```shell
> CHECKOV_EXPERIMENTAL_TERRAFORM_MANAGED_MODULES=True checkov -d .
> ```

### Scanning Private Terraform Modules

If you have modules stored in a private repository or a private Terraform registry (hosted on Terraform Cloud, Terraform Enterprise or a third-party provider like GitLab), you can grant Checkov access by providing access tokens as environment variables. This will enable Checkov to attempt to clone and scan those modules.

| Variable Name          | Description                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| GITHUB_PAT             | Github personal access token with read access to the private repository                          |
| BITBUCKET_TOKEN        | Bitbucket personal access token with read access to the private repository                       |
| TF_HOST_NAME           | (defaults to app.terraform.io) Terraform registry host name. Example: gitlab.com / example.com   |
| TFC_TOKEN\*            | (deprecated, use TF_REGISTRY_TOKEN) Terraform Cloud token which can access the private registry  |
| TF_REGISTRY_TOKEN      | Private registry access token (supports Terraform Cloud / Enterprise and third-party registries) |
| BITBUCKET_USERNAME     | Bitbucket username (can only be used with a BITBUCKET_APP_PASSWORD)                              |
| BITBUCKET_APP_PASSWORD | Bitbucket app password (can only be used with a BITBUCKET_USERNAME)                              |

For self-hosted VCS repositories, use the following environment variables:

| Variable Name | Description                                          |
| ------------- | ---------------------------------------------------- |
| VCS_BASE_URL  | Base URL of the self-hosted VCS: https://example.com |
| VCS_USERNAME  | Username for basic authentication                    |
| VCS_TOKEN     | Password for basic authentication                    |

#### Examples

- Terraform Cloud registry private module scan

```shell
# TF_HOST_NAME will default to app.terraform.io
export TF_REGISTRY_TOKEN=xxxxxx
checkov -d . --download-external-modules true
```

- Terraform Enterprise registry private module scan

```shell
export TF_HOST_NAME=tfe.example.com
export TF_REGISTRY_TOKEN=xxxxxx
checkov -d . --download-external-modules true
```

- Gitlab registry public module scan

```shell
export TF_HOST_NAME=gitlab.com
checkov -d . --download-external-modules true
```

- Gitlab self-hosted registry private module scan

```shell
# A job token or a personal access token with the read_api scope is required
export TF_HOST_NAME=gitlab.example.com
export TF_REGISTRY_TOKEN=xxxxxx
checkov -d . --download-external-modules true
```
