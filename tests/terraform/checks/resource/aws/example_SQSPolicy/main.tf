
resource "aws_sqs_queue_policy" "fail" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
                    {
                    "Version": "2012-10-17",
                    "Id": "sqspolicy",
                    "Statement": [
                        {
                        "Sid": "First",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "*",
                        "Resource": "${aws_sqs_queue.q.arn}",
                        "Condition": {
                            "ArnEquals": {
                            "aws:SourceArn": "${aws_sns_topic.example.arn}"
                            }
                        }
                        }
                    ]
                    }
                    POLICY
}

resource "aws_sqs_queue_policy" "pass" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
                    {
                    "Version": "2012-10-17",
                    "Id": "sqspolicy",
                    "Statement": [
                        {
                        "Sid": "First",
                        "Effect": "Allow",
                        "Principal": "ARN:01010101010:TEST:SAMPLE",
                        "Action": "sqs:SendMessage",
                        "Resource": "${aws_sqs_queue.q.arn}",
                        "Condition": {
                            "ArnEquals": {
                            "aws:SourceArn": "${aws_sns_topic.example.arn}"
                            }
                        }
                        }
                    ]
                    }
                    POLICY
}

