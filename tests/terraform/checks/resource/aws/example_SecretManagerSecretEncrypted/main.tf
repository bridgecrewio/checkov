# pass

resource "aws_secretsmanager_secret" "enabled1" {
  name = "secret"

  kms_key_id = var.kms_key_id
}

resource "aws_secretsmanager_secret" "enabled2" {
  name = "secret"

  kms_key_id = "1234"
}

# failure

resource "aws_secretsmanager_secret" "default" {
  name = "secret"
}

resource "aws_secretsmanager_secret" "default_explicit" {
  name = "secret"
  kms_key_id = "alias/aws/secretsmanager"
}
