resource "aws_ecs_cluster" "fail4" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.example.arn
    }
  }
  tags = { test = "fail" }
}

resource "aws_ecs_cluster" "unknown" {
  name = "white-hart"
  tags = { test = "fail" }
}

resource "aws_ecs_cluster" "unknown2" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      # kms_key_id = aws_kms_key.example.arn
      logging = "NONE"

      log_configuration {
        # cloud_watch_encryption_enabled = true
        # cloud_watch_log_group_name     = aws_cloudwatch_log_group.example.name

        # or
        # s3_bucket_name=   and
        # s3_bucket_encryption_enabled =true
      }
    }
  }
  tags = { test = "fail" }
}

resource "aws_ecs_cluster" "fail" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      # kms_key_id = aws_kms_key.example.arn

      log_configuration {
        # cloud_watch_encryption_enabled = true
        # cloud_watch_log_group_name     = aws_cloudwatch_log_group.example.name

        # or
        # s3_bucket_name=   and
        # s3_bucket_encryption_enabled =true
      }
    }
  }
  tags = { test = "fail" }
}



resource "aws_ecs_cluster" "fail2" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.example.arn

      log_configuration {
        # cloud_watch_encryption_enabled = true
        # cloud_watch_log_group_name     = aws_cloudwatch_log_group.example.name

        # or
        # s3_bucket_name=   and
        # s3_bucket_encryption_enabled =true
      }
    }
  }
  tags = { test = "fail" }
}

resource "aws_ecs_cluster" "fail3" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.example.arn

      log_configuration {
        cloud_watch_encryption_enabled = false
        # cloud_watch_log_group_name     = aws_cloudwatch_log_group.example.name

        # or
        # s3_bucket_name=   and
        # s3_bucket_encryption_enabled =true
      }
    }
  }
  tags = { test = "fail" }
}

resource "aws_ecs_cluster" "fail5" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.example.arn

      log_configuration = [null]
    }
  }
  tags = { test = "fail" }
}

resource "aws_ecs_cluster" "pass" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.example.arn

      log_configuration {
        cloud_watch_encryption_enabled = true
        # cloud_watch_log_group_name     = aws_cloudwatch_log_group.example.name

        # or
        # s3_bucket_name=   and
        # s3_bucket_encryption_enabled =true
      }
    }
  }
  tags = { test = "fail" }
}

resource "aws_ecs_cluster" "pass2" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.example.arn

      log_configuration {
        #        cloud_watch_encryption_enabled = true
        # cloud_watch_log_group_name     = aws_cloudwatch_log_group.example.name

        # or
        # s3_bucket_name=   and
        s3_bucket_encryption_enabled = true
      }
    }
  }
  tags = { test = "fail" }
}