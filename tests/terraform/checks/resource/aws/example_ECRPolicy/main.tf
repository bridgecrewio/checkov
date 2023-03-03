provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecr_repository" "public" {
  name = "public_repo"
}

resource "aws_ecr_repository_policy" "fail" {
  repository = aws_ecr_repository.public.name
  policy     = <<POLICY
{   "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "new policy",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",                
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",                
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",                
                "ecr:DescribeRepositories",                
                "ecr:GetRepositoryPolicy",                
                "ecr:ListImages",                
                "ecr:DeleteRepository",
                "ecr:BatchDeleteImage",                
                "ecr:SetRepositoryPolicy",
                "ecr:DeleteRepositoryPolicy"
            ]        
        }   
    ]
    }
POLICY
}

resource "aws_ecr_repository" "private" {
  name = "private_repo"
}

resource "aws_ecr_repository_policy" "pass" {
  repository = aws_ecr_repository.private.name
  policy     = <<POLICY
{   "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "new policy",
            "Effect": "Allow",
            "Principal": {"AWS": [
                "arn:aws:iam::123456789012:user/pull-user-1",
                "arn:aws:iam::123456789012:user/pull-user-2"]},
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",                
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",                
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",                
                "ecr:DescribeRepositories",                
                "ecr:GetRepositoryPolicy",                
                "ecr:ListImages",                
                "ecr:DeleteRepository",
                "ecr:BatchDeleteImage",                
                "ecr:SetRepositoryPolicy",
                "ecr:DeleteRepositoryPolicy"
            ]        
        }   
    ]
    }
POLICY
}


resource "aws_ecr_repository" "empty" {
  name = "nopolicy_repo"
}

resource "aws_ecr_repository_policy" "empty" {
  repository = aws_ecr_repository.empty.name
  policy     = ""
}

resource "aws_ecr_repository" "conditional_ok" {
  name = "conditional_ok_repo"
}

resource "aws_ecr_repository_policy" "pass_conditional" {
  repository = aws_ecr_repository.conditional_ok.name
  policy     = <<POLICY
{   "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "new policy",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",                
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",                
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",                
                "ecr:DescribeRepositories",                
                "ecr:GetRepositoryPolicy",                
                "ecr:ListImages",                
                "ecr:DeleteRepository",
                "ecr:BatchDeleteImage",                
                "ecr:SetRepositoryPolicy",
                "ecr:DeleteRepositoryPolicy"
            ],        
            "Condition": {
                "ForAllValues:StringEquals": {
                    "aws:PrincipalOrgID": "o-12345678"
                }
            }
        }   
    ]
    }
POLICY
}

resource "aws_ecr_repository" "conditional_bad" {
  name = "conditional_bad_repo"
}

resource "aws_ecr_repository_policy" "fail_conditional" {
  repository = aws_ecr_repository.conditional_bad.name
  policy     = <<POLICY
{   "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "new policy",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",                
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",                
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",                
                "ecr:DescribeRepositories",                
                "ecr:GetRepositoryPolicy",                
                "ecr:ListImages",                
                "ecr:DeleteRepository",
                "ecr:BatchDeleteImage",                
                "ecr:SetRepositoryPolicy",
                "ecr:DeleteRepositoryPolicy"
            ],
            "Condition": {
                "ForAllValues:StringEquals": {
                    "aws:username": "pull-user-1"
                }
            }
        }   
    ]
    }
POLICY
}

resource "aws_ecr_repository_policy" "cond_any_pass" {
  repository = "example"

  policy = jsonencode(
    {
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
          ],
          Condition = {
            "ForAnyValue:StringEquals" = {
              "aws:PrincipalOrgID" = local.org_ids
            }
          }
        }
      ]
    }
  )
}

resource "aws_ecr_repository_policy" "pass_without_principal" {
  repository = "example"

  policy = jsonencode(
    {
      Version   = "2008-10-17",
      Statement = [
        {
          Effect    = "Allow",
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
              "aws:PrincipalOrgID" = local.org_ids
            }
          }
        }
      ]
    }
  )
}

resource "aws_ecr_repository_policy" "cond_equals_pass" {
  repository = "example"

  policy = jsonencode(
    {
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
          ],
          Condition = {
            "StringEquals" = {
              "aws:PrincipalOrgID" = "o-xxxxxxxxxxx"
            }
          }
        }
      ]
    }
  )
}
