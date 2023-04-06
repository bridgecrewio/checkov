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

resource "aws_iam_role" "fail3" {
  name               = "fail-default"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = [
            "arn:aws:iam::123456789012:role/role-name",
            "123456789012"
          ]
        }
      }
    ]
  })
}

resource "aws_iam_role" "fail4" {
  name               = "fail-default"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = [
            "arn:aws:iam::123456789012:role/role-name"
          ]
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = [
            "123456789012",
          ]
        }
      }
    ]
  })
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

resource "aws_iam_role" "pass3" {
  name               = "fail-default"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Deny"
        Sid    = ""
        Principal = {
          AWS = [
            "123456789012"
          ]
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = [
            "arn:aws:iam::123456789012:role/role-name",
          ]
        }
      }
    ]
  })
}
