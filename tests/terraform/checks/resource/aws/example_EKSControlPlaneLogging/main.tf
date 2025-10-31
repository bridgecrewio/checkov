# pass

resource "aws_eks_cluster" "fully_enabled" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
}

resource "aws_eks_cluster" "fully_enabled_with_dynamic_block" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]

  dynamic "encryption_config" {
    for_each = [1]

    content {
      provider {
        key_arn = "aws/kms/key"
      }
      resources = ["secrets"]
    }
  }
}

# fail

resource "aws_eks_cluster" "partially_enabled" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  enabled_cluster_log_types = [
    "api",
    "audit"
  ]
}

resource "aws_eks_cluster" "not_configured" {
  name     = "example"
  role_arn = "aws_iam_role.arn"
}
