---
layout: default
published: true
title: Sharing Custom Policies
nav_order: 5
---

# Sharing Custom Policies

[Custom Policies](https://www.checkov.io/3.Custom%20Policies/Custom%20Policies%20Overview.html) can be reused across multiple projects. 

You can download a git repository containing custom checks: 

```python
checkov --external-checks-git  https://github.com/bridgecrewio/checkov.git
```

## Sub-directories

If you want to download only a specific subdirectory from a GitHub repository, you can specify a subdirectory after a double-slash` //`. Checkov will first download the URL specified before the double-slash (as if you didn’t specify a double-slash), but will then copy the path after the double slash into a temporal directory.

```text
checkov --external-checks-git  https://github.com/bridgecrewio/checkov.git//tests/terraform/checks/resource/registry/example_external_dir/extra_checks
```

For example, if you’re downloading this GitHub repository, but you only want to download the “extra_checks” directory, you can do the following:

`https://github.com/bridgecrewio/checkov.git//extra_checks`

Note: Checkov will execute Python code. Only use trusted sources when executing external checks.
