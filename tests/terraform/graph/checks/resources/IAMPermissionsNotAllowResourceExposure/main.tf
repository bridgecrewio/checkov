resource "aws_iam_policy" "policy_pass" {
  name        = "policy_pass"
  path        = "/"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
        "Action": "s3:GetObject",
        "Effect": "Allow",
        "Resource": "*"
        }
    ]
  })
}

# Test standard IAM Policy - fail
resource "aws_iam_policy" "policy_fail" {
  name        = "policy_fail"
  path        = "/"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
        "Action": "acm-pca:CreatePermission",
        "Effect": "Allow",
        "Resource": "*"
        }
    ]
  })
}

# Test standard IAM Policy with a Deny - pass
resource "aws_iam_policy" "policy_pass2" {
  name        = "policy_pass2"
  path        = "/"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
        "Action": "acm-pca:CreatePermission",
        "Effect": "Deny",
        "Resource": "*"
        }
    ]
  })
}

# Test standard IAM Policy with a heredoc - fail
resource "aws_iam_policy" "policy_fail2" {
  name = "policy_fail2"
  path = "/"

  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
    {
      "Action": "acm-pca:DeletePolicy",
      "Effect": "Allow",
      "Resource": "*",
      "Sid": ""
    }
    ]
  }
POLICY
}

# Test standard IAM Policy with mutiple actions - fail
resource "aws_iam_policy" "policy_mutiple_actions_fail" {
  name        = "fail"
  path        = "/"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
        "Action": [
          "acm-pca:DeletePolicy",
          "s3:GetObject"
        ]
        "Effect": "Allow",
        "Resource": "*"
        }
    ]
  })
}

# Test Role Policy - pass
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy
resource "aws_iam_role_policy" "pass1" {
  name = "pass1"
  role = aws_iam_role.test_role.id

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "ec2:DescribeInstances"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

# Test Role Policy - fail
resource "aws_iam_role_policy" "fail1" {
  name = "fail1"
  role = aws_iam_role.test_role.id

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "xray:Put*",
          "ec2:DescribeInstances"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

# Test Group Policy - pass
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_group_policy
resource "aws_iam_group_policy" "pass1" {
  name  = "my_developer_policy"
  group = aws_iam_group.my_developers.name

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:Describe*",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

# Test Group Policy - fail
resource "aws_iam_group_policy" "fail1" {
  name  = "my_developer_policy"
  group = aws_iam_group.my_developers.name

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:Describe*",
          "iam:*",
          "xray:Put*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

# Test User Policy - pass
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy
resource "aws_iam_user_policy" "pass1" {
  name = "test"
  user = aws_iam_user.lb.name

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:Describe*",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

# Test User Policy - fail
resource "aws_iam_user_policy" "fail1" {
  name = "test"
  user = aws_iam_user.lb.name

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

# Test SSOAdmin Permissions Set Inline Policy - pass
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssoadmin_permission_set_inline_policy
resource "aws_ssoadmin_permission_set_inline_policy" "pass1" {
  instance_arn       = aws_ssoadmin_permission_set.example.instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.example.arn
  inline_policy      = <<POLICY
{
  "Statement": [
    {
      "Action": [
        "s3:ListBucket*",
        "s3:HeadBucket",
        "s3:Get*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::b1",
        "arn:aws:s3:::b1/*",
        "arn:aws:s3:::b2",
        "arn:aws:s3:::b2/*"
      ],
      "Sid": ""
    },
    {
      "Action": "s3:GetObject*",
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::b1/*",
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}

# Test SSOAdmin Permissions Set Inline Policy - fail
resource "aws_ssoadmin_permission_set_inline_policy" "fail1" {
  instance_arn       = aws_ssoadmin_permission_set.example.instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.example.arn
  inline_policy      = <<POLICY
{
  "Statement": [
    {
      "Action": [
        "s3:HeadBucket",
        "acm-pca:DeletePolicy"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::b1",
        "arn:aws:s3:::b1/*",
        "*"
      ],
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}
