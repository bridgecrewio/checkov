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

resource "aws_s3_bucket" "bucket_unknown" {
  bucket = "bucket_unknown"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm     = var.bla
      }
    }
  }
}

resource "aws_s3_bucket" "bucket_good_5" {
  bucket = "bucket_good"

  dynamic "server_side_encryption_configuration" {
    for_each = var.s3_bucket_encryption_enabled ? [1] : []
  
    content {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm = "AES256"
        }
      }
    }
  }
}

resource "aws_s3_bucket" "bucket_good_6" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket" "bucket_unknown2" {
  bucket = "bucket_unknown"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.mykey.arn
        sse_algorithm     = "${var.whatever}"
      }
    }
  }
}

resource "aws_s3_bucket" "bucket_unknown3" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket" "default_encryption_bucket" {
  bucket = "default_encryption_bucket"
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

resource "aws_s3_bucket" "bucket_bad_5" {
  bucket = "bucket_good"

  dynamic "server_side_encryption_configuration" {
    for_each = var.s3_bucket_encryption_enabled ? [1] : []
  
    content {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm = "jack daniels"
        }
      }
    }
  }
}

resource "aws_s3_bucket" "bucket_bad_6" {
  bucket = "bucket_bad_6"
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

resource "aws_s3_bucket_server_side_encryption_configuration" "good_sse_3" {
  bucket = aws_s3_bucket.bucket_good_6.bucket

  dynamic "rule" {
    for_each = var.s3_bucket_encryption_enabled ? [1] : []
    content {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "unknown_sse_4" {
  bucket = aws_s3_bucket.bucket_unknown3.bucket

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.mykey.arn
      sse_algorithm     = "${var.whatever}"
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

resource "aws_s3_bucket_server_side_encryption_configuration" "bad_sse_3" {
  bucket = aws_s3_bucket.bucket_bad_6.bucket

  dynamic "rule" {
    for_each = var.s3_bucket_encryption_enabled ? [1] : []
    content {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "johnnie walker"
      }
    }
  }
}