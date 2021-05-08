resource "aws_athena_workgroup" "pass" {
  name = "wg-encrypted"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://mys3bucket"
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = "mykmsarn"
      }
    }
  }
}

resource "aws_athena_workgroup" "fail" {
  name = "wg-non-encrypted"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://mys3bucket"
    }
  }
}

