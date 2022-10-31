resource "aws_neptune_cluster" "dynamic_renderd" {
  cluster_identifier                  = "aurora-cluster-demo"
  engine                              = "neptune"
  backup_retention_period             = 5
  preferred_backup_window             = "07:00-09:00"
  skip_final_snapshot                 = true
  apply_immediately                   = true
  dynamic "iam_database_authentication_enabled" {
    for_each = var.dynamic.storage_encrypted
    content {
      iam_database_authentication_enabled = iam_database_authentication_enabled.value
    }
  }
  dynamic "storage_encrypted" {
    for_each = var.dynamic.storage_encrypted
    content {
      storage_encrypted = storage_encrypted.value
    }
  }
}