---
layout: default
published: true
title: Pre-Commit
nav_order: 6
---

# Pre-Commit

To use Checkov with [pre-commit](https://pre-commit.com), just add the following to your local repo's `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/bridgecrewio/checkov.git
  rev: '' # change to tag or sha
  hooks:
    - id: checkov
```

Make sure to change `rev:` to be either a git commit sha or tag of checkov containing `.pre-commit-hooks.yaml`. Note that local environment variables will apply when using pre-commit hooks. In urgent situations, pre-commit hooks can be skipped with the `--no-verify` flag.

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

## Diff scanning pre-commit hook

To let `checkov` only scan the changed files choose the `checkov_diff` hook, which scans against all frameworks:

```yaml
repos:
  - repo: https://github.com/bridgecrewio/checkov.git
    rev: '' # change to tag or sha
    hooks:
      - id: checkov_diff
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
```
