# Integrate Checkov with pre-commit

## Pre-commit Setup

To use checkov with [pre-commit](https://pre-commit.com), just add the following to your local repo's `.pre-commit-config.yaml` file. Make sure to change rev: to be either a git commit sha or tag of checkov containing `.pre-commit-hooks.yaml`.

```yaml
- repo: https://github.com/bridgecrewio/checkov.git
  rev: '' # change to tag or sha
  hooks:
    - id: checkov
```

## How to add custom parameters

You can provide arguments to `checkov` using the args property.  For example, the following will print checkov output, and proceed regardless of success/failure to the next pre-commit check.

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
