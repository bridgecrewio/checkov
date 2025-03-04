resource "aws_s3_bucket" "example" {
  # bucket is not encrypted
  bucket = "untugged"
}

resource "aws_s3_bucket_replication_configuration" "replication" {
  depends_on = [aws_s3_bucket_versioning.bad_bucket]
  role   = aws_iam_role.bad_bucket_replication.arn
  bucket = aws_s3_bucket.example.id
  rule {
    id     = "foobar"
    status = "Disabled"
    destination {
      bucket        = aws_s3_bucket.bad_bucket_destination.arn
      storage_class = "STANDARD"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bad_sse" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey.arn
      sse_algorithm     = "aws:kms"
    }
  }
}