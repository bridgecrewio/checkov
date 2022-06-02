# pass

resource "aws_s3_bucket" "enabled" {
  bucket = "example"

  replication_configuration {
    role = aws_iam_role.replication.arn

    rules {
      id     = "example"
      status = "Enabled"

      filter {
        tags = {}
      }
      destination {
        bucket        = aws_s3_bucket.destination.arn
        storage_class = "STANDARD"

        replication_time {
          status  = "Enabled"
          minutes = 15
        }

        metrics {
          status  = "Enabled"
          minutes = 15
        }
      }
    }
  }
}

resource "aws_s3_bucket" "enabled_var" {
  bucket = "example"

  replication_configuration {
    role = aws_iam_role.replication.arn

    rules {
      id     = "foobar"
      status = var.replication_enabled

      filter {
        tags = {}
      }
      destination {
        bucket        = aws_s3_bucket.destination.arn
        storage_class = "STANDARD"

        replication_time {
          status  = "Enabled"
          minutes = 15
        }

        metrics {
          status  = "Enabled"
          minutes = 15
        }
      }
    }
  }
}

resource "aws_s3_bucket" "unknown_var" {
  bucket = "example"

  replication_configuration {
    role = aws_iam_role.replication.arn

    rules {
      id     = "foobar"
      status = var.unknown_var

      filter {
        tags = {}
      }
      destination {
        bucket        = aws_s3_bucket.destination.arn
        storage_class = "STANDARD"

        replication_time {
          status  = "Enabled"
          minutes = 15
        }

        metrics {
          status  = "Enabled"
          minutes = 15
        }
      }
    }
  }
}

variable "unknown_var" {
  description = "unknown value"
}


variable "replication_enabled" {
  default = "Enabled"
}

resource "aws_s3_bucket" "legacy_syntax" {
  bucket = "example"

  replication_configuration {
    role = aws_iam_role.replication.arn

    rules {
      id     = "foobar"
      status = "${var.unknown_var}"

      filter {
        tags = {}
      }
      destination {
        bucket        = aws_s3_bucket.destination.arn
        storage_class = "STANDARD"

        replication_time {
          status  = "Enabled"
          minutes = 15
        }

        metrics {
          status  = "Enabled"
          minutes = 15
        }
      }
    }
  }
}

# fail

resource "aws_s3_bucket" "default" {
  bucket = "example"
}

resource "aws_s3_bucket" "disabled" {
  bucket = "example"

  replication_configuration {
    role = aws_iam_role.replication.arn

    rules {
      id     = "foobar"
      status = "Disabled"

      filter {
        tags = {}
      }
      destination {
        bucket        = aws_s3_bucket.destination.arn
        storage_class = "STANDARD"

        replication_time {
          status  = "Enabled"
          minutes = 15
        }

        metrics {
          status  = "Enabled"
          minutes = 15
        }
      }
    }
  }
}

# provider version 4

resource "aws_s3_bucket" "enabled_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_replication_configuration" "enabled_v4" {
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.enabled_v4.id

  rule {
    id = "foobar"

    filter {
      prefix = "foo"
    }

    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.destination.arn
      storage_class = "STANDARD"
    }
  }
}

resource "aws_s3_bucket" "disabled_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_replication_configuration" "disabled_v4" {
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.disabled_v4.id

  rule {
    id = "foobar"

    filter {
      prefix = "foo"
    }

    status = "Disabled"

    destination {
      bucket        = aws_s3_bucket.destination.arn
      storage_class = "STANDARD"
    }
  }
}

resource "aws_s3_bucket" "legacy_syntax_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_replication_configuration" "legacy_syntax_v4" {
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.legacy_syntax_v4.id

  rule {
    id = "foobar"

    filter {
      prefix = "foo"
    }

    status = "${var.whatever}"

    destination {
      bucket        = aws_s3_bucket.destination.arn
      storage_class = "STANDARD"
    }
  }
}
