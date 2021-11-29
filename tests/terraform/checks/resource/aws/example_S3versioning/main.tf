
resource "aws_s3_bucket" "fail4" {
  region        = "us-west-2"
  bucket        = "my_bucket"
  acl           = "public-read"
  force_destroy = true
  tags {
    Name = "my-bucket"
  }
}


resource "aws_s3_bucket" "fail3" {
  region        = "us-west-2"
  bucket        = "my_bucket"
  acl           = "public-read"
  force_destroy = true
  tags          = { Name = "my-bucket" }
  enabled       = True
}

resource "aws_s3_bucket" "fail2" {
  region        = "us-west-2"
  bucket        = "my_bucket"
  acl           = "public-read"
  force_destroy = true
  tags = {
    Name = "my-bucket"
    wrong_field = {
    enabled = true }
  }
}

resource "aws_s3_bucket" "fail" {
  region        = "us-west-2"
  bucket        = "my_bucket"
  acl           = "public-read"
  force_destroy = true
  tags          = { Name = "my-bucket" }
  wrong_field   = { versioning = { enabled = true } }
}


resource "aws_s3_bucket" "pass" {
  region        = "us-west-2"
  bucket        = "my_bucket"
  acl           = "public-read"
  force_destroy = true

  tags = { Name = "my-bucket" }

  logging {
    target_bucket = "logging-bucket"
    target_prefix = "log/"
  }
  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket" "failcomplex" {
  acl    = "public-read-write"
  bucket = "superfail"

  versioning {
    enabled    = false
    mfa_delete = false
  }

  policy = <<POLICY
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"AddCannedAcl",
      "Effect":"Allow",
      "Principal": "*",
      "Action":["s3:PutObject","s3:PutObjectAcl"],
      "Resource":"arn:aws:s3:::superfail/*"
    },
    {
        "Principal": {
            "AWS": ["*"],
            "Effect": "Deny",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "*"
            ]
        }
    }
  ]
}
POLICY
}


resource "aws_s3_bucket" "this" {
  bucket = var.bucket
  acl    = "private"
  versioning {
    enabled = var.enabled
  }
}

variable "enabled" {
  default=true
}