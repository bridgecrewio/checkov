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