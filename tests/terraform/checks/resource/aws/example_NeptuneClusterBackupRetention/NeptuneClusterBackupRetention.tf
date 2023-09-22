## SHOULD PASS: backup retention to 7 or more
resource "aws_neptune_cluster" "ckv_unittest_pass" {
  cluster_identifier                  = "neptune-cluster-demo"
  engine                              = "neptune"
  backup_retention_period             = 7
}

## SHOULD FAIL: backup retention to less than 7
resource "aws_neptune_cluster" "ckv_unittest_fail_not_adequate" {
  cluster_identifier                  = "neptune-cluster-demo"
  engine                              = "neptune"
  backup_retention_period             = 3
}

## SHOULD FAIL: backup retention not set (default is 1)
resource "aws_neptune_cluster" "ckv_unittest_fail_default" {
  cluster_identifier                  = "neptune-cluster-demo"
  engine                              = "neptune"
}