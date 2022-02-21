# fail
resource "aws_backup_vault" "backup" {
  name = "example_backup_vault"
}

# pass
resource "aws_backup_vault" "backup_with_kms_key" {
  name        = "example_backup_vault"
  kms_key_arn = aws_kms_key.example.arn
}