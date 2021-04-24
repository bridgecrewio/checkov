# pass

resource "aws_secretsmanager_secret" "enabled" {
  name = "secret"

  kms_key_id = var.kms_key_id
}

# failure

resource "aws_secretsmanager_secret" "default" {
  name = "secret"
}
