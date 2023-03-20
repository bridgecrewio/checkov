resource "aws_secretsmanager_secret_rotation" "pass" {
  secret_id           = aws_secretsmanager_secret.pass.id
  rotation_lambda_arn = aws_lambda_function.example.arn

  rotation_rules {
    automatically_after_days = 30
  }
}

resource "aws_secretsmanager_secret" "pass" {
  name = "pike"
}

resource "aws_secretsmanager_secret" "fail" {
  name = "sato"
}