# pass

resource "aws_codebuild_project" "enabled" {
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
}

# fail

resource "aws_codebuild_project" "default" {
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

# unknown

resource "aws_codebuild_project" "no_artifacts" {
  name         = "example"
  service_role = "aws_iam_role.example.arn"

  artifacts {
    type = "NO_ARTIFACTS"
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
