# fail
resource "aws_sqs_queue" "fail" {
  name = "fail"
}

resource "aws_sqs_queue_policy" "fail" {
  queue_url = aws_sqs_queue.fail.id
  
  policy = jsonencode({
    Version = "2012-10-17",
    Id = "AllowAllSendMessage",
    Statement = [
      {
        Effect = "Allow",
        Principal = "*",
        Action = "sqs:SendMessage",
        Resource = aws_sqs_queue.fail.arn
      }
    ]
  })
}

resource "aws_sqs_queue" "fail2" {
  name = "fail2"
}

resource "aws_sqs_queue_policy" "fail2" {
  queue_url = aws_sqs_queue.fail2.id

  policy = jsonencode({
    Version = "2012-10-17",
    Id = "AllowAllSendMessage",
    Statement = [
      {
        Effect = "Allow",
        Principal = "*",
        Action = "*",
        Resource = aws_sqs_queue.fail.arn
      }
    ]
  })
}

# pass
resource "aws_sqs_queue" "pass" {
  name = "pass"
}

resource "aws_sqs_queue_policy" "pass" {
  queue_url = aws_sqs_queue.pass.id

  policy = jsonencode({
    Version = "2012-10-17",
    Id = "RestrictedSendMessage",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::123456789012:role/specific-role"
        },
        Action = "sqs:SendMessage",
        Resource = aws_sqs_queue.pass.arn
      }
    ]
  })
}

resource "aws_sqs_queue" "pass_w_condition" {
  name = "pass_w_condition"
}

resource "aws_sqs_queue_policy" "pass_w_condition" {
  queue_url = aws_sqs_queue.pass_w_condition.id

  policy = jsonencode({
    Version = "2012-10-17",
    Id = "ConditionalAllowSendMessage",
    Statement = [
      {
        Effect = "Allow",
        Principal = "*",
        Action = "sqs:SendMessage",
        Resource = aws_sqs_queue.pass_w_condition.arn,
        Condition = {
          StringEquals = {
            "aws:SourceVpc": "vpc-12345678"
          }
        }
      }
    ]
  })
}