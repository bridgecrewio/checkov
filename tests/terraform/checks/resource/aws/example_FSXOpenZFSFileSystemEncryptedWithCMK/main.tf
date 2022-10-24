resource "aws_fsx_openzfs_file_system" "pass" {
  storage_capacity                = var.file_system.storage_capacity
  subnet_ids                      = var.subnet_ids
  deployment_type                 = var.file_system.deployment_type
  throughput_capacity             = var.file_system.throughput_capacity
  kms_key_id                      = var.kms_key_id
  automatic_backup_retention_days = 0 #flag as no bckup
}

resource "aws_fsx_openzfs_file_system" "fail" {
  storage_capacity                = var.file_system.storage_capacity
  subnet_ids                      = var.subnet_ids
  deployment_type                 = var.file_system.deployment_type
  throughput_capacity             = var.file_system.throughput_capacity
  automatic_backup_retention_days = 0 #flag as no bckup
}