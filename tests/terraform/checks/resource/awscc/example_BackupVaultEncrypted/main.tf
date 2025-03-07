resource "awscc_backup_backup_vault" "pass" {
  backup_vault_name  = "pass"
  encryption_key_arn = awscc_kms_key.example.arn
}

resource "awscc_backup_backup_vault" "fail" {
  backup_vault_name  = "fail"
}