---
layout: default
published: true
title: Pre-Commit
nav_order: 6
---

# Pre-Commit

If you want to automatically run `checkov` when files in your git repo change, [install the pre-commit binary](https://pre-commit.com/#install), and add a [.pre-commit-config.yaml file](https://github.com/bridgecrewio/checkov/blob/main/.pre-commit-config.yaml) to your project with content similar to the example below.

Note that depending on the hook id you select for pre-commit hooks, you may need to provide the following:

* For the `python` hooks, pre-commit 3.x is able to provide [python](https://pre-commit.com/#python) without additional dependencies.
* For the `container` hooks, the [Docker](https://docs.docker.com/get-docker/) CLI and a container runtime must be available.


```yaml
- repo: https://github.com/bridgecrewio/checkov.git
  rev: '' # change to tag or sha
  hooks:
    - id: checkov
      # - id: checkov_container
      # - id: checkov_diff
      # - id: checkov_diff_container
      # - id: checkov_secrets
      # - id: checkov_secrets_container
```

Make sure to change `rev:` to be either a git commit sha or tag of checkov containing `.pre-commit-hooks.yaml`. Note that local environment variables will apply when using pre-commit hooks. In urgent situations, pre-commit hooks can be skipped with the `--no-verify` flag.

After adding the hooks to `.pre-commit-config.yaml` run the following command(s):

```bash
pre-commit install --install-hooks
```

or

```bash
pre-commit install
pre-commit install-hooks
```

## Adding Custom Parameters

By default, the Checkov pre-commit hook runs when there are changes to `.tf` files. This can be modified by overriding the file parameter:

```yaml
repos:
  - repo: https://github.com/bridgecrewio/checkov.git
    rev: '' # change to tag or sha
    hooks:
      - id: checkov
        files: \.y(a)?ml$  # any kind of regex of file types you are interested to trigger the pre-commit hook
```


You can use the `args` property to input arguments to Checkov. In the example below, Checkov output will be printed, and then Checkov will proceed to the next pre-commit check *regardless of success/failure*.

```yaml
repos:
- repo: https://github.com/bridgecrewio/checkov.git
  rev: '' # change to tag or sha
  hooks:
  - id: checkov
    verbose: true
    args: [--soft-fail]
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v3.2.0
  hooks:
  - id: trailing-whitespace
```

Similarly, to specify custom policies installed in the `checks` directory of your repository, use the following:

```yaml
repos:
- repo: https://github.com/bridgecrewio/checkov.git
  rev: '' # change to tag or sha
  hooks:
  - id: checkov
    args: [--external-checks-dir, 'checks']
```

Or you can override the entry altogether:

```yaml
repos:
  - repo: https://github.com/bridgecrewio/checkov.git
    rev: '' # change to tag or sha
    hooks:
      - id: checkov
        entry: checkov -d . --skip-check CKV_AWS_123
```

When using the `diff` or `secrets` hooks, the last argument _must_ be `-f` due to how `checkov` and `pre-commit` interact:

```yaml
      - id: checkov_secrets_container
        args:
          - '--quiet'
          - '-f' # required and must come last
```

By default, the container based pre-commit hooks use the `latest` tag. This can be overridden by declaring the version number in the entry field in the pre-commit config.

```yaml
    hooks:
      - id: checkov_container
        entry: bridgecrew/checkov:2.4.2 -d .
## Diff scanning pre-commit hook

To let `checkov` only scan the changed files choose the `checkov_diff` hook, which scans against all frameworks:

```yaml
repos:
  - repo: https://github.com/bridgecrewio/checkov.git
    rev: '' # change to tag or sha
    hooks:
      - id: checkov_diff
      # - id: checkov_diff_container
```

if you want to customize this hook, you need to override the `entry` field, because the file flag `-f` has to be at the end:

```yaml
repos:
  - repo: https://github.com/bridgecrewio/checkov.git
    rev: '' # change to tag or sha
    hooks:
      - id: checkov_diff
        entry: checkov --framework terraform -f
```

## Secrets scanning pre-commit hook

Checkov also natively has a secrets only pre-commit hook that scans all files just for secrets:

```yaml
repos:
  - repo: https://github.com/bridgecrewio/checkov.git
    rev: '' # change to tag or sha
    hooks:
      - id: checkov_secrets
      # - id: checkov_secrets_container
```
