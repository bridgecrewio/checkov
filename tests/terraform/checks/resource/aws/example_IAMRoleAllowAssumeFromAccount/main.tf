resource "aws_iam_role" "fail" {
  name               = "fail-default"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": { "AWS": "123123123123" },
      "Effect": "Allow",
      "Sid": ""
    }]
}
POLICY
}

resource "aws_iam_role" "fail2" {
  name               = "fail-default"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [{
    "Action": "sts:AssumeRole",
    "Principal": {"AWS": "arn:aws:iam::123123123123:root"},
    "Effect": "Allow",
    "Sid": ""
  }]
}
POLICY
}


resource "aws_iam_role" "pass2" {
  name               = "pass2-default"
  assume_role_policy = ""
}

resource "aws_iam_role" "pass" {
  name = "pass-default"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [{
    "Action": "sts:AssumeRole",
    "Principal": { "Service": "ecs-tasks.amazonaws.com"    },
    "Effect": "Allow",
    "Sid": ""
  }]
}
POLICY
}

