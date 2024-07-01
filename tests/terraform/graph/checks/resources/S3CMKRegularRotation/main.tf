# Pass

resource "aws_kms_key" "mykey1" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
  is_enabled = true
  enable_key_rotation = true
}

resource "aws_s3_bucket" "mybucket1" {
  bucket = "mybucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pass" {
  bucket = aws_s3_bucket.mybucket1.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey1.arn
      sse_algorithm     = "aws:kms"
    }
  }
}


# Fail - not enabled

resource "aws_kms_key" "mykey2" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
  is_enabled = false
  enable_key_rotation = true
}

resource "aws_s3_bucket" "mybucket2" {
  bucket = "mybucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "fail_disabled" {
  bucket = aws_s3_bucket.mybucket2.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey2.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Fail - no rotation

resource "aws_kms_key" "mykey3" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
  is_enabled = true
  enable_key_rotation = false
}

resource "aws_s3_bucket" "mybucket3" {
  bucket = "mybucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "fail_no_rotation" {
  bucket = aws_s3_bucket.mybucket3.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey3.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Fail - no rotation

resource "aws_s3_bucket" "mybucket4" {
  bucket = "mybucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "fail_no_kms" {
  bucket = aws_s3_bucket.mybucket4.id
}