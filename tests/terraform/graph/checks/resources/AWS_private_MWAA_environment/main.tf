# PASS 1: webserver_access_mode = PRIVATE_ONLY

resource "aws_iam_role" "pud_pass_role" {
  name = "pud_pass_role"
  assume_role_policy = jsonencode({
    Version = "2023-09-27"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    tag-key = "pud_checkov_pass"
  }
}

resource "aws_s3_bucket" "pud_pass_bucket" {
  bucket = "pud_pass_bucket"
}

resource "aws_mwaa_environment" "pud_mwaa_env_pass" {
  dag_s3_path        = "dags/"
  execution_role_arn = aws_iam_role.pud_pass_role.arn
  name               = "pud_mwaa_env_pass"
  webserver_access_mode = "PRIVATE_ONLY"
  source_bucket_arn = aws_s3_bucket.pud_pass_bucket.arn
}

# PASS 2: webserver_access_mode Not mentioned. DEFAULT = PRIVATE_ONLY

resource "aws_iam_role" "pud_pass_role_1" {
  name = "pud_pass_role_1"
  assume_role_policy = jsonencode({
    Version = "2023-09-27"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    tag-key = "pud_checkov_pass_1"
  }
}

resource "aws_s3_bucket" "pud_pass_bucket_1" {
  bucket = "pud_pass_bucket_1"
}

resource "aws_mwaa_environment" "pud_mwaa_env_pass_1" {
  dag_s3_path        = "dags/"
  execution_role_arn = aws_iam_role.pud_pass_role.arn
  name               = "pud_mwaa_env_pass_1"
  source_bucket_arn = aws_s3_bucket.pud_pass_bucket.arn
}

# FAIL: webserver_access_mode = PUBLIC_ONLY

resource "aws_iam_role" "pud_fail_role" {
  name = "pud_fail_role"
  assume_role_policy = jsonencode({
    Version = "2023-09-27"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    tag-key = "pud_checkov_fail"
  }
}

resource "aws_s3_bucket" "pud_fail_bucket" {
  bucket = "pud_fail_bucket"
}

resource "aws_mwaa_environment" "pud_mwaa_env_fail" {
  dag_s3_path        = "dags/"
  execution_role_arn = aws_iam_role.pud_fail_role.arn
  name               = "pud_mwaa_env_fail"
  webserver_access_mode = "PUBLIC_ONLY"
  source_bucket_arn = aws_s3_bucket.pud_fail_bucket.arn
}

