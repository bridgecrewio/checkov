---
layout: default
published: true
title: Contribute YAML-based Policies
order: 3
---

# Contributing YAML-based Custom Policies
1. Define a policy as described [here](doc:create-custom-policy-yaml-attribute-check-and-composite).
2. Create a branch under the `checkov2` fork (will be changed + the URLs after merge) - `https://github.com/nimrodkor/checkov`
3. Add `<policy_name>.yaml` file to `https://github.com/nimrodkor/checkov/tree/master/checkov/graph/terraform/checks` inside the relevant provider folder that matches your current policy.

## Example
`checkov/terraform/checks/graph_checks/aws/EBSAddedBackup.yaml`

[block:code]
{
  "codes": [
    {
      "code": "metadata:\n  name: \"Ensure that EBS are added in the backup plans of AWS Backup\"\n  id: \"CKV2_AWS_9\"\n  category: \"BACKUP_AND_RECOVERY\"\ndefinition:\n  and:\n    - cond_type: connection\n      resource_types:\n        - aws_backup_selection\n      connected_resource_types:\n        - aws_ebs_volume\n      operator: exists\n    - cond_type: filter\n      attribute: resource_type\n      value:\n        - aws_ebs_volume\n      operator: within",
      "language": "yaml",
      "name": " "
    }
  ]
}
[/block]

# YAML Format Testing
1 - Add the test resources directory to: `https://github.com/nimrodkor/checkov/tree/master/tests/graph/terraform/checks/resources` and create a folder with the same name as your Custom Policy. In this folder, add the Terraform file(s) which are resources for testing the policy, and `expected.yaml` - all the resources that should pass and the resources that should fail.

## Terraform Files Example 
`tests/graph/terraform/checks/resources/EBSAddedBackup/main.tf`
[block:code]
{
  "codes": [
    {
      "code": "resource \"aws_ebs_volume\" \"ebs_good\" {\n  availability_zone = \"us-west-2a\"\n  size              = 40\n \n  tags = {\n    Name = \"HelloWorld\"\n  }\n}\n \nresource \"aws_ebs_volume\" \"ebs_bad\" {\n  availability_zone = \"us-west-2a\"\n  size              = 40\n \n  tags = {\n    Name = \"HelloWorld\"\n  }\n}\n \nresource \"aws_backup_selection\" \"backup_good\" {\n  iam_role_arn = \"arn\"\n  name         = \"tf_example_backup_selection\"\n  plan_id      = \"123456\"\n \n  resources = [\n    aws_ebs_volume.ebs_good.arn\n  ]\n}\n \nresource \"aws_backup_selection\" \"backup_bad\" {\n  iam_role_arn = \"arn\"\n  name         = \"tf_example_backup_selection\"\n  plan_id      = \"123456\"\n \n  resources = [\n  ]\n}\n",
      "language": "yaml",
      "name": " "
    }
  ]
}
[/block]

## 'expected.yaml' File Example
 
`tests/graph/terraform/checks/resources/EBSAddedBackup/expected.yaml`
[block:code]
{
  "codes": [
    {
      "code": "pass:\n  - \"aws_ebs_volume.ebs_good\"\nfail:\n  - \"aws_ebs_volume.ebs_bad\"",
      "language": "yaml",
      "name": " "
    }
  ]
}
[/block]
 
2 - Add the test call into tests file - 
`tests/graph/terraform/checks/test_yaml_policies.py`
### Example
[block:code]
{
  "codes": [
    {
      "code": "...\n    def test_EBSAddedBackup(self):\n        self.go(\"EBSAddedBackup\")\n...\n",
      "language": "yaml",
      "name": " "
    }
  ]
}
[/block]
