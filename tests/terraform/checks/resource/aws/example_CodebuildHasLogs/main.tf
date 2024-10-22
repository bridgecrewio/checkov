# pass

resource "aws_codebuild_project" "pass" {
  name         = "example"
  service_role = "aws_iam_role.example.arn"

  encryption_key = "aws_kms_key.scanner_key.id"

  artifacts {
    type = "S3"
  }
  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "docker:dind"
    type         = "LINUX_CONTAINER"
  }
  source {
    type = "NO_SOURCE"
  }
  logs_config {
    s3_logs {

    }
  }
}

# fail

resource "aws_codebuild_project" "fail" {
  name         = "example"
  service_role = "aws_iam_role.example.arn"

  artifacts {
    type = "S3"
  }
  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "docker:dind"
    type         = "LINUX_CONTAINER"
  }
  source {
    type = "NO_SOURCE"
  }
}
