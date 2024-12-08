resource "aws_s3_bucket" "multi-line-multi-checks" {
  region        = "var.region"
    #checkov:skip=CKV_AWS_93,CKV_AWS_21:Skip all
    #checkov:skip=CKV_AWS_145:The bucket is a public static content host
  bucket        = "local.bucket_name"
  force_destroy = true
  acl           = "public-read"
}

resource "aws_s3_bucket" "multi-line-no-comment" {
  region        = "var.region"
    #checkov:skip=CKV_AWS_93:
    #checkov:skip=CKV_AWS_145:The bucket is a public static content host
  bucket        = "local.bucket_name"
  force_destroy = true
  acl           = "public-read"
}

resource "aws_s3_bucket" "one-line-one-check" {
  region        = "var.region"
    #checkov:skip=CKV_AWS_145:The bucket is a public static content host
  bucket        = "local.bucket_name"
  force_destroy = true
  acl           = "public-read"
}

resource "aws_s3_bucket" "one-line-multi-checks" {
  region        = "var.region"
    #checkov:skip=CKV_AWS_93,CKV_AWS_145:skip all
  bucket        = "local.bucket_name"
  force_destroy = true
  acl           = "public-read"
}

resource "aws_s3_bucket" "no-comment" {
  region = "var.region"
  bucket = "local.bucket_name"
  force_destroy = true
  acl           = "public-read"
}
