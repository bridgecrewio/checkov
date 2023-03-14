resource "aws_scheduler_schedule" "fail" {
  name       = "my-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(1 hour)"

  target {
    arn      = aws_sqs_queue.example.arn
    role_arn = aws_iam_role.example.arn
  }
}

resource "aws_scheduler_schedule" "fail2" {
  name       = "my-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(1 hour)"
  kms_key_arn         = ""

  target {
    arn      = aws_sqs_queue.example.arn
    role_arn = aws_iam_role.example.arn
  }
}

resource "aws_scheduler_schedule" "pass" {
  name       = "my-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(1 hour)"
  kms_key_arn         = "arn:aws:kms:eu-west-2:680235478471:key/a61e2553-18fe-40b8-a959-bf775459ed46"

  target {
    arn      = aws_sqs_queue.example.arn
    role_arn = aws_iam_role.example.arn
  }
}
resource "aws_scheduler_schedule" "pass2" {
  name       = "my-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "rate(1 hour)"
  kms_key_arn         = aws_kms_key.pike.arn

  target {
    arn      = aws_sqs_queue.example.arn
    role_arn = aws_iam_role.example.arn
  }
}