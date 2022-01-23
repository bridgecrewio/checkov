# pass

resource "aws_eks_cluster" "disabled" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    endpoint_public_access = False
  }
}

resource "aws_eks_cluster" "restricted" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    public_access_cidrs = ["10.0.0.0/16"]
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

resource "aws_eks_cluster" "empty" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    public_access_cidrs = []
  }
}

resource "aws_eks_cluster" "open" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    public_access_cidrs = ["0.0.0.0/0"]
  }
}
