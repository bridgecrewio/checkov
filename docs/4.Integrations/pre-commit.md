# Integrate Checkov with pre-commit

## Pre-commit Setup

To use checkov with pre-commit, just add the following to your local repo's `.pre-commit-config.yaml` file. Make sure to change rev: to be either a git commit sha or tag of checkov containing `.pre-commit-hooks.yaml`.

```
- repo: https://github.com/bridgecrewio/checkov.git
  rev: master
  hooks:
    - id: checkov
      files: \.tf$
```
