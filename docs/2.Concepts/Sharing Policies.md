---
layout: default
published: true
title: Sharing Policies
order: 7
---

# Sharing Policies

[Custom policies](Custom%20Policies.md) can be reused across multiple projects. 

You can download git repository containing custom checks: 

```bash
checkov --external-checks-git  https://github.com/bridgecrewio/checkov.git
```

# Sub directories 
```bash
checkov --external-checks-git  https://github.com/bridgecrewio/checkov.git//tests/terraform/checks/resource/registry/example_external_dir/extra_checks
```
If you want to download only a specific subdirectory from a git repository, you can specify a subdirectory after a double-slash //. (inspired by [go-getter](https://github.com/hashicorp/go-getter)) 
checkov will first download the URL specified before the double-slash (as if you didn't specify a double-slash), but will then copy the path after the double slash into temporal directory.

For example, if you're downloading this GitHub repository, but you only want to download the "extra_checks" directory, you can do the following:

`https://github.com/bridgecrewio/checkov.git//extra_checks`