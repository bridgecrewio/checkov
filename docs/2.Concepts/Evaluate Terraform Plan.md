---
layout: default
published: true
title: Evaluate Checkov policies on Terraform plan
order: 8
---
# Evaluate Checkov policies on Terraform plan

Checkov supports the evaluation of policies on resources declared in `.tf` files. And also evaluation of `terraform plan` json files. 
Plan has more context and is more complete in resolved values and should can be a choice of usage. 
Terraform plan files might contain arguments (like secrets) that are injected dynamically.

## Example

```bash
terraform init
terraform plan --out tfplan.binary
terraform show -json tfplan.binary > tfplan.json

checkov -f tfplan.json

```
### Example output:

![Checkov terraform plan scan](checkov_terraform_plan.png)
