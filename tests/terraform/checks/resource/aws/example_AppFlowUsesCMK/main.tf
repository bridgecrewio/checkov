resource "aws_appflow_flow" "fail" {
  name = "example"

  source_flow_config {
    connector_type = "S3"
    source_connector_properties {
      s3 {
        bucket_name   = aws_s3_bucket_policy.example_source.bucket
        bucket_prefix = "example"
      }
    }
  }

  destination_flow_config {
    connector_type = "S3"
    destination_connector_properties {
      s3 {
        bucket_name = aws_s3_bucket_policy.example_destination.bucket

        s3_output_format_config {
          prefix_config {
            prefix_type = "PATH"
          }
        }
      }
    }
  }

  task {
    source_fields     = ["exampleField"]
    destination_field = "exampleField"
    task_type         = "Map"

    connector_operator {
      s3 = "NO_OP"
    }
  }

  trigger_config {
    trigger_type = "OnDemand"
  }
}

resource "aws_appflow_flow" "pass" {
  name = "example"

  source_flow_config {
    connector_type = "S3"
    source_connector_properties {
      s3 {
        bucket_name   = aws_s3_bucket_policy.example_source.bucket
        bucket_prefix = "example"
      }
    }
  }

  destination_flow_config {
    connector_type = "S3"
    destination_connector_properties {
      s3 {
        bucket_name = aws_s3_bucket_policy.example_destination.bucket

        s3_output_format_config {
          prefix_config {
            prefix_type = "PATH"
          }
        }
      }
    }
  }

  task {
    source_fields     = ["exampleField"]
    destination_field = "exampleField"
    task_type         = "Map"

    connector_operator {
      s3 = "NO_OP"
    }
  }

  kms_arn = aws_kms_key.example.arn

  trigger_config {
    trigger_type = "OnDemand"
  }
}
