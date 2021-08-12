resource "aws_codebuild_project" "fail" {
  name = "fail-project"
  artifacts {
    type                = S3
    encryption_disabled = true
  }

}

resource "aws_codebuild_project" "no_artifacts_encryption_ignored" {
  name = "no-art-project"
  artifacts {
    type                = "NO_ARTIFACTS"
    encryption_disabled = true
  }
}

resource "aws_codebuild_project" "success_no_encryption_disabled" {
  name = "default-project"
  artifacts {
    type = "S3"
  }
}

resource "aws_codebuild_project" "success" {
  name = "success-project"
  artifacts {
    type                = "S3"
    encryption_disabled = false
  }
}
