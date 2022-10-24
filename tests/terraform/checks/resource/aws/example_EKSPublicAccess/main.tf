# pass

resource "aws_eks_cluster" "disabled" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    endpoint_public_access = False
  }
}

# fail

resource "aws_eks_cluster" "default" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]
  }
}

resource "aws_eks_cluster" "enabled" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    endpoint_public_access = True
  }
}
