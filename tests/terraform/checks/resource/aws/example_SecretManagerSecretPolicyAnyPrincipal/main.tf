# pass - denies everyone, so a wildcard principal is safe here
resource "aws_secretsmanager_secret_policy" "sm_pass_deny" {
  secret_arn = aws_secretsmanager_secret.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
       {
          "Principal": "*",
          "Effect": "Deny",
          "Action": [
            "secretsmanager:GetSecretValue"
          ],
          "Resource": "*"
       }
    ]
}
POLICY
}

# pass - wildcard principal is scoped by a Condition
resource "aws_secretsmanager_secret_policy" "sm_pass_condition" {
  secret_arn = aws_secretsmanager_secret.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
       {
          "Sid": "AllowFromSourceAccountOnly",
          "Principal": {
            "AWS": [
                "arn:aws:iam::123456789101:role/reader",
                "*"
            ]
          },
          "Effect": "Allow",
          "Action": [
            "secretsmanager:GetSecretValue"
          ],
          "Resource": "*",
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

# pass - specific principal ARN, no wildcard
resource "aws_secretsmanager_secret_policy" "sm_pass_specific" {
  secret_arn = aws_secretsmanager_secret.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
       {
          "Principal": {
            "AWS": "arn:aws:iam::123456789101:role/reader"
          },
          "Effect": "Allow",
          "Action": [
            "secretsmanager:GetSecretValue"
          ],
          "Resource": "*"
       }
    ]
}
POLICY
}

# fail - wildcard string principal allowed, anyone can read the secret
resource "aws_secretsmanager_secret_policy" "sm_fail_star" {
  secret_arn = aws_secretsmanager_secret.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
       {
          "Principal": "*",
          "Effect": "Allow",
          "Action": [
            "secretsmanager:GetSecretValue"
          ],
          "Resource": "*"
       }
    ]
}
POLICY
}

# fail - AWS wildcard principal allowed
resource "aws_secretsmanager_secret_policy" "sm_fail_aws_star" {
  secret_arn = aws_secretsmanager_secret.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
       {
          "Principal": {
            "AWS": "*"
          },
          "Effect": "Allow",
          "Action": [
            "secretsmanager:GetSecretValue"
          ],
          "Resource": "*"
       }
    ]
}
POLICY
}

# fail - wildcard mixed into the principal list with no Condition to scope it
resource "aws_secretsmanager_secret_policy" "sm_fail_list_star" {
  secret_arn = aws_secretsmanager_secret.test.arn

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
       {
          "Principal": {
            "AWS": [
                "arn:aws:iam::123456789101:role/reader",
                "*"
            ]
          },
          "Effect": "Allow",
          "Action": [
            "secretsmanager:GetSecretValue"
          ],
          "Resource": "*"
       }
    ]
}
POLICY
}
