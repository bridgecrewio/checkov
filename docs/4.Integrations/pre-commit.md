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

Make sure to change `rev:` to be either a git commit sha or tag of checkov containing `.pre-commit-hooks.yaml`.

## Adding Custom Parameters

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
