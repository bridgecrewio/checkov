resource "aws_s3_bucket_policy" "pass1" {
  bucket = ""
}

resource "aws_s3_bucket_policy" "pass2" {
  policy = jsonencode({
    Version   = "2008-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          "AWS": "some-arn"
        },
        Action    = [
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetDownloadUrlForLayer",
          "ecr:ListImages"
        ]
      }
    ]
  })
  bucket = ""
}

resource "aws_s3_bucket_policy" "fail" {
  policy = jsonencode({
    Version   = "2008-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = [
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetDownloadUrlForLayer",
          "ecr:ListImages"
        ]
      }
    ]
  })
  bucket = ""
}

resource "aws_s3_bucket_policy" "fail2" {
  policy = jsonencode({
    Version   = "2008-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          "AWS": "*"
        },
        Action    = [
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetDownloadUrlForLayer",
          "ecr:ListImages"
        ]
      }
    ]
  })
  bucket = ""
}

resource "aws_s3_bucket_policy" "pass3" {
  policy = jsonencode({
    Version   = "2008-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          "AWS": "*"
        },
        Action    = [
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetDownloadUrlForLayer",
          "ecr:ListImages"
        ],
        Condition = {
          "ForAnyValue:StringEquals" = {
            "aws:PrincipalOrgID" = "some-org-id"
          }
        }
      }
    ]
  })
  bucket = ""
}

resource "aws_s3_bucket_policy" "pass4" {
  policy = jsonencode({
    Version   = "2008-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          "AWS": "*"
        },
        NotAction    = [
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetDownloadUrlForLayer",
          "ecr:ListImages"
        ],
        Condition = {
          "ForAnyValue:StringEquals" = {
            "aws:PrincipalOrgID" = "some-org-id"
          }
        }
      }
    ]
  })
  bucket = ""
}
