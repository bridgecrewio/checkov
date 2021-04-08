---
layout: default
published: true
title: Contribute YAML-based Policies
nav_order: 3
---

# Contributing YAML-based Custom Policies

1. Define a policy as described [here](../3.Custom%20Policies/YAML%20Custom%20Policies.md).
2. Create a branch under the `checkov2` fork (will be changed + the URLs after merge) - `https://github.com/nimrodkor/checkov`
3. Add `<policy_name>.yaml` file to `https://github.com/nimrodkor/checkov/tree/master/checkov/graph/terraform/checks` inside the relevant provider folder that matches your current policy.

## Example
`checkov/terraform/checks/graph_checks/aws/EBSAddedBackup.yaml`

```yaml
metadata:
  name: "Ensure that EBS are added in the backup plans of AWS Backup"
  id: "CKV2_AWS_9"
  category: "BACKUP_AND_RECOVERY"
definition:
  and:
    - cond_type: connection
      resource_types:
        - aws_backup_selection
      connected_resource_types:
        - aws_ebs_volume
      operator: exists
    - cond_type: filter
      attribute: resource_type
      value:
        - aws_ebs_volume
      operator: within
```

## YAML Format Testing
1 - Add the test resources directory to: `https://github.com/nimrodkor/checkov/tree/master/tests/graph/terraform/checks/resources` and create a folder with the same name as your Custom Policy. In this folder, add the Terraform file(s) which are resources for testing the policy, and `expected.yaml` - all the resources that should pass and the resources that should fail.

### Terraform Files Example 
`tests/graph/terraform/checks/resources/EBSAddedBackup/main.tf`

```yaml
resource "aws_ebs_volume" "ebs_good" {
  availability_zone = "us-west-2a"
  size              = 40
 
  tags = {
    Name = "HelloWorld"
  }
}
 
resource "aws_ebs_volume" "ebs_bad" {
  availability_zone = "us-west-2a"
  size              = 40
 
  tags = {
    Name = "HelloWorld"
  }
}
 
resource "aws_backup_selection" "backup_good" {
  iam_role_arn = "arn"
  name         = "tf_example_backup_selection"
  plan_id      = "123456"
 
  resources = [
    aws_ebs_volume.ebs_good.arn
  ]
}
 
resource "aws_backup_selection" "backup_bad" {
  iam_role_arn = "arn"
  name         = "tf_example_backup_selection"
  plan_id      = "123456"
 
  resources = [
  ]
}

```

## 'expected.yaml' File Example
 
`tests/graph/terraform/checks/resources/EBSAddedBackup/expected.yaml`

```yaml
pass:
  - "aws_ebs_volume.ebs_good"
fail:
  - "aws_ebs_volume.ebs_bad"
```
 
2 - Add the test call into tests file - 
`tests/graph/terraform/checks/test_yaml_policies.py`
### Example

```yaml
...
    def test_EBSAddedBackup(self):
        self.go("EBSAddedBackup")
...

```
