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

resource "aws_eks_cluster" "restricted_ipv6" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    public_access_cidrs = ["2001:db8::/32"]
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

resource "aws_eks_cluster" "open_ipv6" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    public_access_cidrs = ["::/0"]
  }
}

resource "aws_eks_cluster" "open_ipv6_expanded" {
  name     = "example"
  role_arn = "aws_iam_role.arn"

  vpc_config {
    subnet_ids = ["subnet-12345"]

    public_access_cidrs = ["0000:0000:0000:0000:0000:0000:0000:0000/0"]
  }
}
