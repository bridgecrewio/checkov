# pass

resource "aws_iam_policy" "restrictable" {
  policy = <<POLICY
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
          "s3:*",
        ],
        "Resource": "arn:aws:s3:::bucket"
      }
      ]
    }
POLICY
}

resource "aws_iam_policy" "unrestrictable" {
  policy = <<POLICY
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
          "xray:PutTelemetryRecords",
          "xray:PutTraceSegments",
        ],
        "Resource": "*"
      }
      ]
    }
POLICY
}

# fail

resource "aws_iam_policy" "fail" {
  policy = <<POLICY
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
          "s3:*",
        ],
        "Resource": "*"
      }
      ]
    }
POLICY
}

# unknown

