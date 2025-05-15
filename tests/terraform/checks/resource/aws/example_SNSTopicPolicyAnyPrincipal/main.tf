# pass
resource "aws_sns_topic_policy" "sns_tp1" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "*",
          "Effect": "Deny",
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

resource "aws_sns_topic_policy" "sns_pass_condition" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Sid": "AllowSpecificPrincipalsFromSourceAccount",
           "Principal": {
            "AWS": [
                "arn:aws:iam::123456789101:role/sns",
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
            "SNS:AddPermission"
          ],
          "Resource": "${aws_sns_topic.test.arn}",
          "Condition": {
            "StringEquals": {
              "aws:SourceAccount": "123456789101"
            }
          }
       }
    ]
}
POLICY
}

# should return as unknown dou to condition parsing error.
resource "aws_sns_topic_policy" "sns_tp_unknown" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "*",
          "Effect": "Deny",
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
          "Resource": "${aws_sns_topic.test.arn}",
          "Condition": {'StringEquals': 'AWS:SourceOwner'}
       }
    ]
}
POLICY
}


# fail
resource "aws_sns_topic_policy" "sns_tp2" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": { 
            "AWS": [
                "arn:aws:iam::123456789101:role/sns", 
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

# fail
resource "aws_sns_topic_policy" "sns_tp3" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": { 
            "AWS": "arn:aws:iam::*:role/sns"
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

# fail
resource "aws_sns_topic_policy" "sns_tp4" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": { 
            "AWS": "*"
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

# fail
resource "aws_sns_topic_policy" "sns_tp5" {
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

# pass
resource "aws_sns_topic_policy" "sns_tp6" {
  arn = aws_sns_topic.test.arn

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "arn:aws:iam::123456789101:role/sns",
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