resource "aws_flow_log" "example" {
  iam_role_arn    = "arn"
  log_destination      = "arn:aws:s3:::test-bucket"
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.ok_vpc.id
}

resource "aws_flow_log" "example1" {
  iam_role_arn    = "arn"
  log_destination = "log"
  traffic_type    = "ALL"
  log_destination_type = "s3"
  vpc_id          = aws_vpc.ok_vpc.id
}

resource "aws_flow_log" "example2" {
  iam_role_arn    = "arn"
  log_destination = "log"
  traffic_type    = "ALL"
  log_destination_type = "s3"
  vpc_id          = aws_vpc.not_ok_vpc2.id
}

resource "aws_flow_log" "example3" {
  iam_role_arn    = "arn"
  log_destination      = "arn:aws:s3:::test-bucket"
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.ok_vpc1.id
}

resource "aws_flow_log" "example4" {
  iam_role_arn    = "arn"
  log_destination      = "arn:aws:s3:::test-bucket"
  log_destination_type = "log"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.ok_vpc1.id
}

resource "aws_flow_log" "example5" {
  iam_role_arn    = "arn"
  log_destination      = "name"
  log_destination_type = "log"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.ok_vpc1.id
}

resource "aws_flow_log" "example6" {
  iam_role_arn    = "arn"
  log_destination      = "name1"
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.ok_vpc1.id
}

resource "aws_vpc" "not_ok_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "ok_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "not_ok_vpc2" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "ok_vpc1" {
  cidr_block = "10.0.0.0/16"
}

