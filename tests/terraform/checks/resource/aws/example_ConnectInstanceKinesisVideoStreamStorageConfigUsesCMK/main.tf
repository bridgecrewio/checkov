resource "aws_connect_instance_storage_config" "pass" {
  instance_id   = aws_connect_instance.pass.id
  resource_type = "MEDIA_STREAMS"

  storage_config {
    kinesis_video_stream_config {
      prefix                 = "pass"
      retention_period_hours = 3

      encryption_config {
        encryption_type = "KMS"
        key_id          = aws_kms_key.test.arn
      }
    }
    storage_type = "KINESIS_VIDEO_STREAM"
  }
}


resource "aws_connect_instance_storage_config" "fail" {
  instance_id   = aws_connect_instance.fail.id
  resource_type = "MEDIA_STREAMS"

  storage_config {
    kinesis_video_stream_config {
      prefix                 = "fail"
      retention_period_hours = 3

      encryption_config {
        encryption_type = "KMS"
      }
    }
    storage_type = "KINESIS_VIDEO_STREAM"
  }
}