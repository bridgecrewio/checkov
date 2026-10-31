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


# Managed query results are encrypted with an AWS owned key by default
resource "aws_athena_workgroup" "pass_managed_results" {
  name = "wg-managed-results"

  configuration {
    enforce_workgroup_configuration = true

    managed_query_results_configuration {
      enabled = true
    }
  }
}

resource "aws_athena_workgroup" "pass_managed_results_kms" {
  name = "wg-managed-results-kms"

  configuration {
    managed_query_results_configuration {
      enabled = true
      encryption_configuration {
        kms_key = "mykmsarn"
      }
    }
  }
}

# Managed query results disabled: the S3 result location must be encrypted
resource "aws_athena_workgroup" "fail_managed_results_disabled" {
  name = "wg-managed-results-disabled"

  configuration {
    managed_query_results_configuration {
      enabled = false
    }

    result_configuration {
      output_location = "s3://mys3bucket"
    }
  }
}
