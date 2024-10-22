provider "aws" {
    region="us-east-1"
}

resource "aws_sqs_queue" "sqs" {
    name = "sqs_nc_notprinc_all"
    sqs_managed_sse_enabled = false
}

resource "aws_sqs_queue_policy" "test" {
    queue_url = aws_sqs_queue.sqs.id
    policy = <<POLICY
       {
          "Version": "2008-10-17",
          "Id": "__default_policy_ID",
          "Statement": [ {
              "Sid": "statement1",
              "Effect": "Allow",
              "NotPrincipal": {
                 "AWS": "arn:aws:iam::0000:root"
              },
              "Action": "SQS:*",
              "Resource": "${aws_sqs_queue.sqs.arn}"
          }
          ]
       }
    POLICY
}