locals {
  role_arn  = var.role_arn == "" ? aws_iam_role.pipeline.0.arn : var.role_arn
  role_name = var.role_arn == "" ? "AWSCodePipelineServiceRole-${data.aws_region.current.name}-${var.name}" : ""
}

locals {
  artifact_store = {
    location = "codepipeline-${data.aws_region.current.name}-${data.aws_caller_identity.current.account_id}"
  type = "S3" }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}