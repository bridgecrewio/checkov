---
layout: default
published: true
title: Terraform Plan Scanning
nav_order: 8
---

# Terraform Plan Scanning

## Evaluate Checkov Policies on Terraform Plan
Checkov supports the evaluation of policies on resources declared in `.tf` files. It can also be used to evaluate `terraform plan` expressed in a json file. Plan evaluation provides Checkov additional dependencies and context that can result in a more complete scan result. Since Terraform plan files may contain arguments (like secrets) that are injected dynamically, it is advised to run a plan evaluation using Checkov in a secure CI/CD pipeline setting.

### Example

The example below creates a Terraform Plan JSON file and scans it using Checkov. It uses `jq` which must be installed beforehand and leads to better formatted outputs and results. It is not explicitly required for plan scanning.

```json
terraform init
terraform plan --out tfplan.binary
terraform show -json tfplan.binary | jq > tfplan.json

checkov -f tfplan.json
```


The output would look like:
```
checkov -f tf.json
Check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enabled"
	FAILED for resource: aws_s3_bucket.customer
	File: /tf/tf1.json:224-268
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-16-enable-versioning

		225 |               "values": {
		226 |                 "acceleration_status": "",
		227 |                 "acl": "private",
		228 |                 "arn": "arn:aws:s3:::mybucket",
```

### Ignored checks

Since the Terraform checks are used for both normal templates and plan files, some of those are not applicable for a plan file.
They evaluate the `lifecycle` block, which is only relevant for the CLI and are not stored in the plan file itself.

Following checks will be ignored;
- CKV_AWS_217 
- CKV_AWS_233
- CKV_AWS_237 
- CKV_GCP_82

### Deleted resources

To check if a resource will be deleted or changed (further change values can be found [here](https://www.terraform.io/internals/json-format#change-representation)) the change actions values can be accessed via the attribute name `__change_actions__`.

Ex. Python
```python
    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        actions = conf.get("__change_actions__")
        if isinstance(actions, list) and "delete" in actions:
            return CheckResult.FAILED
        return CheckResult.PASSED
```

Ex. YAML
```yaml
  cond_type: attribute
  resource_types:
    - aws_secretsmanager_secret
  attribute: __change_actions__
  operator: not_contains
  value: delete
```

### Changed resource fields

To write a check conditional on whether or not a specific field has changed, one can access the changed fields via the attribute `TF_PLAN_RESOURCE_CHANGE_KEYS` (a list of changed keys).

Ex Python
```python
from checkov.terraform.plan_parser import TF_PLAN_RESOURCE_CHANGE_ACTIONS, TF_PLAN_RESOURCE_CHANGE_KEYS

def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        actions = conf.get(TF_PLAN_RESOURCE_CHANGE_ACTIONS)
        if isinstance(actions, list) and "update" in actions:
            if "protocol" in conf.get(TF_PLAN_RESOURCE_CHANGE_KEYS):
                return CheckResult.FAILED
        return CheckResult.PASSED
```

## Combining Plan and Terraform scans
Plan file scans can be enriched with the Terraform files to improve outputs, add skip comments and expand coverage. Note that these will increase scan times.

### Enrichment
Using the `--repo-root-for-plan-enrichment` flag, code blocks, and resource IDs in the output will be from the Terraform files and skip comments in the Terraform files will be respected in the Plan file scan.

Example:
```
checkov -f tfplan.json --repo-root-for-plan-enrichment /pathToTF/
```

### Deep Analysis
Using the `--deep-analysis` flag in combination with the `--repo-root-for-plan-enrichment` flag will combine the graph of the Plan file scan and the Terraform files scans. This allows Checkov to make graph connections where there is incomplete information in the Plan file. For example, locals do not have the connections defined in the plan file but can make that connection with the Deep Analysis.

Example:
```
checkov -f tfplan.json --repo-root-for-plan-enrichment /pathToTF/ --deep-analysis
```
