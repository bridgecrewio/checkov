resource "aws_secretsmanager_secret_rotation" "pass" {
  secret_id           = aws_secretsmanager_secret.example.id
  rotation_lambda_arn = aws_lambda_function.example.arn

  rotation_rules {
    automatically_after_days = 30
  }
}

resource "aws_secretsmanager_secret_rotation" "fail" {
  secret_id           = aws_secretsmanager_secret.example.id
  rotation_lambda_arn = aws_lambda_function.example.arn

  rotation_rules {
    automatically_after_days = 90
  }
}

resource "aws_secretsmanager_secret_rotation" "fail_2" {
  secret_id           = aws_secretsmanager_secret.example.id
  rotation_lambda_arn = aws_lambda_function.example.arn

  rotation_rules {
    automatically_after_days = var.days
  }
}

resource "aws_secretsmanager_secret_rotation" "pass_scheduled_hours" {
  secret_id           = aws_secretsmanager_secret.this.id
  rotation_lambda_arn = aws_lambda_function.this.arn

  rotate_immediately = true

  rotation_rules {
    schedule_expression = "rate(4 hours)"
  }

  depends_on = [
    time_sleep.wait_for_lambda_permissions_for_secrets_manager,
    module.rotation_lambda
  ]
}

resource "aws_secretsmanager_secret_rotation" "pass_scheduled_days" {
  secret_id           = aws_secretsmanager_secret.this.id
  rotation_lambda_arn = aws_lambda_function.this.arn

  rotate_immediately = true

  rotation_rules {
    schedule_expression = "rate(89 days)"
  }

  depends_on = [
    time_sleep.wait_for_lambda_permissions_for_secrets_manager,
    module.rotation_lambda
  ]
}

resource "aws_secretsmanager_secret_rotation" "fail_scheduled_days" {
  secret_id           = aws_secretsmanager_secret.this.id
  rotation_lambda_arn = aws_lambda_function.this.arn

  rotate_immediately = true

  rotation_rules {
    schedule_expression = "rate(180 days)"
  }

  depends_on = [
    time_sleep.wait_for_lambda_permissions_for_secrets_manager,
    module.rotation_lambda
  ]
}

resource "aws_secretsmanager_secret_rotation" "pass_scheduled_cron" {
  secret_id           = aws_secretsmanager_secret.this.id
  rotation_lambda_arn = aws_lambda_function.this.arn

  rotate_immediately = true

  rotation_rules {
    schedule_expression = "cron(0 12 * * ? *)"
  }

  depends_on = [
    time_sleep.wait_for_lambda_permissions_for_secrets_manager,
    module.rotation_lambda
  ]
}


# Fail example with cron to be tackled later
# resource "aws_secretsmanager_secret_rotation" "fail_scheduled_cron" {
#   secret_id           = aws_secretsmanager_secret.this.id
#   rotation_lambda_arn = aws_lambda_function.this.arn
#
#   rotate_immediately = true
#
#   rotation_rules {
#     schedule_expression = "cron(0 12 * 2 ? *)"
#   }
#
#   depends_on = [
#     time_sleep.wait_for_lambda_permissions_for_secrets_manager,
#     module.rotation_lambda
#   ]
# }


