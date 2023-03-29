resource "aws_cloudwatch_log_group" "pass" {
  retention_in_days = 365
}

resource "aws_cloudwatch_log_group" "fail" {
  retention_in_days = 5
}
