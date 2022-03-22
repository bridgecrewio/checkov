resource "aws_ecs_cluster" "fail" {
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

resource "aws_ecs_cluster" "pass" {
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

resource "aws_ecs_cluster" "pass2" {
  name = "white-hart"
  configuration {
    execute_command_configuration {
      # kms_key_id = aws_kms_key.example.arn
      logging = "DEFAULT"

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