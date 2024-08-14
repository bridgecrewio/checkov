resource "aws_ssm_parameter" "fail" {
  name        = "/production/database/password/master"
  description = "The parameter description"
  type        = "SecureString"
  value       = var.database_master_password

  tags = {
    environment = "production"
  }
}

resource "aws_ssm_parameter" "pass" {
  name        = "/production/database/password/master"
  description = "The parameter description"
  type        = "SecureString"
  value       = var.database_master_password
  key_id      = aws_kms_key.pike.arn

  tags = {
    environment = "production"
  }
}

resource "aws_ssm_parameter" "pass2" {
  name        = "/production/database/password/master"
  description = "The parameter description"
  type        = "String"
  value       = var.database_master_password

  tags = {
    environment = "production"
  }
}