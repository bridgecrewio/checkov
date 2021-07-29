resource "aws_cloudwatch_log_group" "example" {
  name = "Example"
}

resource "aws_cloudtrail" "aws_cloudtrail_ok" {
  name                          = "tf-trail-foobar"
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.example.arn}:*"
}

resource "aws_cloudtrail" "aws_cloudtrail_not_ok" {
  name                          = "tf-trail-foobar"
}