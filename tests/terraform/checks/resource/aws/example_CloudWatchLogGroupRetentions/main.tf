resource "aws_cloudwatch_log_group" "pass" {
  retention_in_days = 3
}

resource "aws_cloudwatch_log_group" "fail" {}
