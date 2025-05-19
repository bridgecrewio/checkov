# fail
resource "aws_sns_topic_policy" "fail0" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": {
            "AWS": [
                "arn:aws:iam::123456789101:role/sns"
            ]
          },
          "Effect": "Allow",
          "Action": [
            "SNS:Subscribe",
            "SNS:SetTopicAttributes",
            "SNS:RemovePermission",
            "SNS:Receive",
            "SNS:Publish",
            "SNS:ListSubscriptionsByTopic",
            "SNS:GetTopicAttributes",
            "SNS:DeleteTopic",
            "SNS:AddPermission",
          ],
          "Resource": "${aws_sns_topic.test.arn}"
       }
    ]
}
POLICY
}

resource "aws_sns_topic_policy" "fail1" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3ToPublish",
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "SNS:Publish",
            "Resource": "${aws_sns_topic.test.arn}",
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:s3:::your-s3-bucket-name/*"
                },
                "StringEquals": {
                    "aws:SourceAccount": "${data.aws_caller_identity.current.account_id}"
                }
            }
        },
        {
            "Sid": "AllowOriginalAccess",
            "Principal": {
              "AWS": [
                  "arn:aws:iam::123456789101:role/sns"
              ]
            },
            "Effect": "Allow",
            "Action": [
                "SNS:Subscribe",
                "SNS:SetTopicAttributes",
                "SNS:RemovePermission",
                "SNS:Receive",
                "SNS:Publish",
                "SNS:ListSubscriptionsByTopic",
                "SNS:GetTopicAttributes",
                "SNS:DeleteTopic",
                "SNS:AddPermission"
            ],
            "Resource": "${aws_sns_topic.test.arn}"
        }
    ]
}
POLICY
}



# pass
resource "aws_sns_topic_policy" "pass0" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": {
            "AWS": [
                "*"
            ]
          },
          "Effect": "Allow",
          "Action": [
            "SNS:Subscribe",
            "SNS:SetTopicAttributes",
            "SNS:RemovePermission",
            "SNS:Receive",
            "SNS:Publish",
            "SNS:ListSubscriptionsByTopic",
            "SNS:GetTopicAttributes",
            "SNS:DeleteTopic",
            "SNS:AddPermission",
          ],
          "Resource": "${aws_sns_topic.test.arn}"
       }
    ]
}
POLICY
}

resource "aws_sns_topic_policy" "pass1" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "*",
          "Effect": "Allow",
          "Action": [
            "SNS:Subscribe",
            "SNS:SetTopicAttributes",
            "SNS:RemovePermission",
            "SNS:Receive",
            "SNS:Publish",
            "SNS:ListSubscriptionsByTopic",
            "SNS:GetTopicAttributes",
            "SNS:DeleteTopic",
            "SNS:AddPermission",
          ],
          "Resource": "${aws_sns_topic.test.arn}"
       }
    ]
}
POLICY
}

resource "aws_sns_topic_policy" "pass2" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3ToPublish",
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "SNS:Publish",
            "Resource": "${aws_sns_topic.test.arn}",
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:s3:::your-s3-bucket-name/*"
                },
                "StringEquals": {
                    "aws:SourceAccount": "${data.aws_caller_identity.current.account_id}"
                }
            }
        },
        {
            "Sid": "AllowOriginalAccess",
            "Principal": {
              "AWS": [
                  "arn:aws:iam::123456789101:role/sns"
              ]
            },
            "Effect": "Allow",
            "Action": [
                "SNS:Subscribe",
                "SNS:SetTopicAttributes",
                "SNS:RemovePermission",
                "SNS:Receive",
                "SNS:Publish",
                "SNS:ListSubscriptionsByTopic",
                "SNS:GetTopicAttributes",
                "SNS:DeleteTopic",
                "SNS:AddPermission"
            ],
            "Resource": "${aws_sns_topic.test.arn}",
            "Condition": {
                "ArnEquals": {
                    "aws:PrincipalArn": "arn:aws:iam::123456789101:role/sns"
                }
            }
        }
    ]
}
POLICY
}