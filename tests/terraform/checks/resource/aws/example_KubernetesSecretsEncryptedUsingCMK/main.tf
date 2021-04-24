# pass

resource "aws_eks_cluster" "enabled" {
  name     = "eks"
  role_arn = var.role_arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }

  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = var.key_arn
    }
  }
}

# failure

resource "aws_eks_cluster" "default" {
  name     = "eks"
  role_arn = var.role_arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

# unknown

resource "aws_eks_cluster" "not_secrets" {
  name     = "eks"
  role_arn = var.role_arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }

  encryption_config {
    resources = ["something"]
    provider {
      key_arn = var.key_arn
    }
  }
}
