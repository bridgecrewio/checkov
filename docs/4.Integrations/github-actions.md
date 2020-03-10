# Integrate Checkov with Github Actions

You can integrate Checkov into Github Actions. This provides a simple, automatic way of applying policies to your Terraform code both during merge request review and as part of any build process.

## Basic Set-up

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
    strategy:
      matrix:
        python-version: [3.7]
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v1
        with:
          python-version: ${{ matrix.python-version }}
      - name: Test with Checkov
        run: |
          pip install checkov
          checkov -d .
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

The previous error can be fixed by setting the value of encyption to **true**.
![Actions success](actions_success.png)

## Further Reading

For more details on using Python in Github Actions <https://help.github.com/en/actions/language-and-framework-guides/using-python-with-github-actions>.

The test code sample: <https://github.com/JamesWoolfenden/checkov-action>