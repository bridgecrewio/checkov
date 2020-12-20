resource "aws_cloudwatch_log_group" "bad" {
  name = "bad"
}

resource "aws_cloudwatch_log_group" "good" {
  name = "good"
  kms_key_id = "abc"
}
