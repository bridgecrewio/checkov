resource "aws_flow_log" "example" {
  iam_role_arn    = "arn"
  log_destination = "log"
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.ok_vpc.id
}

resource "aws_vpc" "not_ok_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "ok_vpc" {
  cidr_block = "10.0.0.0/16"
}
