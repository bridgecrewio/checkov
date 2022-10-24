# pass
resource "aws_sqs_queue_policy" "q1" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "*",
          "Effect": "Deny",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue_policy" "q2" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": {
            "AWS": [
                "arn:aws:iam::123456789101:role/sqs",
                "*"
            ]
          },
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue_policy" "q3" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": {
            "AWS": "arn:aws:iam::*:role/sqs"
          },
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue_policy" "q4" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": {
            "AWS": "*"
          },
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue_policy" "q5" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "*",
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# pass
resource "aws_sqs_queue_policy" "q6" {
  queue_url = aws_sqs_queue.q.id

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "arn:aws:iam::123456789101:role/sqs",
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# unknown
resource "aws_sqs_queue_policy" "q7" {
  queue_url = aws_sqs_queue.q.id

  policy = data.aws_iam_policy_document.bucket_policy.json
}


# now test aws_sqs_queue
# pass
resource "aws_sqs_queue" "aq1" {

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "*",
          "Effect": "Deny",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue" "aq2" {
  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": {
            "AWS": [
                "arn:aws:iam::123456789101:role/sqs",
                "*"
            ]
          },
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue" "aq3" {

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": {
            "AWS": "arn:aws:iam::*:role/sqs"
          },
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue" "aq4" {

  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
           "Principal": {
            "AWS": "*"
          },
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# fail
resource "aws_sqs_queue" "aq5" {
  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "*",
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# pass
resource "aws_sqs_queue" "aq6" {
  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[
       {
          "Principal": "arn:aws:iam::123456789101:role/sqs",
          "Effect": "Allow",
          "Action": "sqs:SendMessage",
          "Resource": "${aws_sqs_queue_policy.q.arn}"
       }
    ]
}
POLICY
}

# unknown
resource "aws_sqs_queue" "aq7" {
  policy = data.aws_iam_policy_document.bucket_policy.json
}


# unknown
resource "aws_sqs_queue_policy" "aq8" {
  queue_url = "my_url"

  policy = jsonencode({
      Version = "2012-10-17"
      Id = "my_polivy"
      Statement = [for v in [] :
        {
          Sid = "sid"
          Action = [
            "sqs:SendMessage"
          ]
          Principal = "*"
          Effect   = "Allow"
          Resource = "queue"
          Condition = {
            ArnEquals = {
              "aws:SourceArn": "${v}"
            }
          }
        }
      ]
    })

}