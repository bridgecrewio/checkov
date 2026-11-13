terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "6.71.0" }
  }
}
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "AKIAFAKE"
  secret_key                  = "fake"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
}

resource "aws_s3_bucket" "insecureBucket" {
  bucket = "checkov-insecure-bucket"
  tags = {
    Environment = "dev"
  }
}

resource "aws_s3_bucket" "secureBucket" {
  bucket = "checkov-secure-bucket"
}

resource "aws_s3_bucket_public_access_block" "securePab" {
  bucket                  = aws_s3_bucket.secureBucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "secureVersioning" {
  bucket = aws_s3_bucket.secureBucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secureEncryption" {
  bucket = aws_s3_bucket.secureBucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.rotatedKey.arn
    }
  }
}

resource "aws_s3_bucket_logging" "secureLogging" {
  bucket        = aws_s3_bucket.secureBucket.id
  target_bucket = aws_s3_bucket.insecureBucket.id
  target_prefix = "logs/"
}

resource "aws_security_group" "openSg" {
  name        = "open-sg"
  description = "open ssh"
  ingress {
    description = "ssh from anywhere"
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_kms_key" "plainKey" {
  description = "key without rotation"
}

resource "aws_kms_key" "rotatedKey" {
  description             = "key with rotation"
  enable_key_rotation     = true
  deletion_window_in_days = 7
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "root"
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::123456789012:root" }
      Action    = "kms:*"
      Resource  = "*"
    }]
  })
}

resource "aws_db_instance" "db" {
  identifier          = "checkov-db"
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "admin"
  password            = "SuperSecret123!"
  storage_encrypted   = false
  publicly_accessible = true
  skip_final_snapshot = true
}

resource "aws_iam_policy" "adminPolicy" {
  name = "admin-policy"
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "*", Resource = "*" }]
  })
}

resource "aws_instance" "instance" {
  ami                         = "ami-12345678"
  instance_type               = "t3.micro"
  associate_public_ip_address = true
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }
  root_block_device {
    encrypted   = false
    volume_size = 8
  }
  tags = {
    Name = "checkov-instance"
  }
}

resource "aws_sqs_queue" "queue" {
  name = "checkov-queue"
}

resource "aws_dynamodb_table" "table" {
  name         = "checkov-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  attribute {
    name = "id"
    type = "S"
  }
  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_iam_role" "lambdaRole" {
  name = "checkov-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_lambda_function" "fn" {
  function_name = "checkov-fn"
  role          = aws_iam_role.lambdaRole.arn
  runtime       = "python3.12"
  handler       = "index.handler"
  filename      = "app.zip"
  environment {
    variables = {
      STAGE = "dev"
    }
  }
  tracing_config {
    mode = "Active"
  }
}
