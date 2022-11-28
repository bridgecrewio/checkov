resource "aws_connect_instance_storage_config" "pass" {
  instance_id   = aws_connect_instance.pass.id
  resource_type = "CHAT_TRANSCRIPTS"

  storage_config {
    s3_config {
      bucket_name   = aws_s3_bucket.pass.id
      bucket_prefix = "pass"

      encryption_config {
        encryption_type = "KMS"
        key_id          = aws_kms_key.example.arn
      }
    }
    storage_type = "S3"
  }
}

resource "aws_connect_instance_storage_config" "fail" {
  instance_id   = aws_connect_instance.fail.id
  resource_type = "CHAT_TRANSCRIPTS"

  storage_config {
    s3_config {
      bucket_name   = aws_s3_bucket.pass.id
      bucket_prefix = "fail"

      encryption_config {
        encryption_type = "KMS"
      }
    }
    storage_type = "S3"
  }
}