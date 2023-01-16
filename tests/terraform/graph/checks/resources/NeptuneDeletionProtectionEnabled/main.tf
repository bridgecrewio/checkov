resource "aws_neptune_cluster" "pass" {
  cluster_identifier                  = "neptune-cluster-demo"
  engine                              = "neptune"
  backup_retention_period             = 5
  preferred_backup_window             = "07:00-09:00"
  skip_final_snapshot                 = true
  iam_database_authentication_enabled = true
  apply_immediately                   = true
  deletion_protection                 = true
}

resource "aws_neptune_cluster" "fail" {
  cluster_identifier                  = "neptune-cluster-demo"
  engine                              = "neptune"
  backup_retention_period             = 5
  preferred_backup_window             = "07:00-09:00"
  skip_final_snapshot                 = true
  iam_database_authentication_enabled = true
  apply_immediately                   = true
  deletion_protection                 = false
}

# Note: 
# -------
# If 'deletion_protection' parameter is not passed then, by default it takes 'deletion_protection' as disabled.
# Reference: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/neptune_cluster#deletion_protection

resource "aws_neptune_cluster" "fail" {
  cluster_identifier                  = "neptune-cluster-demo"
  engine                              = "neptune"
  backup_retention_period             = 5
  preferred_backup_window             = "07:00-09:00"
  skip_final_snapshot                 = true
  iam_database_authentication_enabled = true
  apply_immediately                   = true
}