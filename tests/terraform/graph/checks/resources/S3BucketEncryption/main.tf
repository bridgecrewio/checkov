resource "aws_s3_bucket" "bucket_good_1" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket" "bucket_good_2" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket" "bucket_good_3" {
  bucket = "bucket_good"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket" "bucket_good_4" {
  bucket = "bucket_good"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm     = var.bla
      }
    }
  }
}

resource "aws_s3_bucket" "bucket_bad_1" {
  bucket = "bucket_bad_1"
}

resource "aws_s3_bucket" "bucket_bad_2" {
  bucket = "bucket_bad_2"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm     = "metallica"
      }
    }
  }
}

resource "aws_s3_bucket" "bucket_bad_3" {
  bucket = "bucket_bad_3"
}

resource "aws_s3_bucket" "bucket_bad_4" {
  bucket = "bucket_bad_4"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "good_sse_1" {
  bucket = aws_s3_bucket.bucket_good_1.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "good_sse_2" {
  bucket = aws_s3_bucket.bucket_good_2.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey.arn
      sse_algorithm     = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bad_sse_1" {
  bucket = aws_s3_bucket.bucket_bad_3.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey.arn
      sse_algorithm     = "iron maiden"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bad_sse_2" {
  bucket = aws_s3_bucket.bucket_bad_4.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey.arn
    }
  }
}