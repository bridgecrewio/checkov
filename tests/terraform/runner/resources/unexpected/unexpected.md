# Unexpected
This folder is for different cases of test runner test data where the input HCL is maybe unexpectedly transformed when you see the json representation.

This area can be used to verify that certain checks are robust in catching issues which can't be caught by unit testing the HCL input level alone.

## eks_node_group_remote_access
### Description
`remote_access` is omitted in HCL. But is represented as `remote_access: [ ]` in the Plan.

This needs to be taken in to account when writing the check.
### HCL Input
```
resource "aws_eks_node_group" "test" {
  cluster_name    = "test"
  node_group_name = "example"
  node_role_arn   = "example-arn"
  subnet_ids      = ["subnet-ids"]
  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }
}
```
### JSON Output
[eks_node_group_remote_access.json](eks_node_group_remote_access.json)
