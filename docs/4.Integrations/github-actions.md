# Integrate Checkov with Github Actions

You can integrate Checkov into Github Actions. This provides a simple, automatic way of applying policies to your Terraform code both during merge request review and as part of any build process.

## Use a checkov action from the marketplace

go to https://github.com/bridgecrewio/checkov-action and use a pre-made action!

## Create your own action: Basic Set-up

Add a new step in the `workflow.yml`.

```tree
├───.github
│   └───workflows
```

Here is a basic example:

```yaml
---
name: Checkov
on:
  push:
    branches:
      - master
jobs:
  build:

    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python 3.8
        uses: actions/setup-python@v1
        with:
          python-version: 3.8
      - name: Test with Checkov
        id: checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: example/examplea
          framework: terraform
```

## Example Results

Any time after you push your code to Github, it will run this job. If Checkov finds any issues, it will fail the build.

### Action Failure

In the original examples code, the file **aws_efs_file_system.sharedstore.tf**

```terraform
resource "aws_efs_file_system" "sharedstore" {
  creation_token = var.efs["creation_token"]

  lifecycle_policy {
    transition_to_ia = var.efs["transition_to_ia"]
  }

  kms_key_id                      = var.efs["kms_key_id"]
  encrypted                       = false
  performance_mode                = var.efs["performance_mode"]
  provisioned_throughput_in_mibps = var.efs["provisioned_throughput_in_mibps"]
  throughput_mode                 = var.efs["throughput_mode"]
}
```

Is not set to be encrypted. This will fail a Checkov test:

![Actions Failure](actions_failure.png)

### Pipeline Success

The previous error can be fixed by setting the value of encryption to **true**.
![Actions success](actions_success.png)

## Further Reading

For more details on using Python in Github Actions <https://help.github.com/en/actions/language-and-framework-guides/using-python-with-github-actions>.

The test code sample: <https://github.com/JamesWoolfenden/terraform-aws-appsync/blob/master/.github/workflows/master.yml>
