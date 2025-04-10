# pass

resource "awscc_eks_cluster" "pass" {
  name     = "example-cluster"
  role_arn = awscc_iam_role.main.arn
  resources_vpc_config = {
    subnet_ids             = ["subnet-xxxx", "subnet-yyyy"]
    endpoint_public_access = false
  }
}

# fail

resource "awscc_eks_cluster" "fail" {
  name     = "example-cluster"
  role_arn = awscc_iam_role.main.arn

  resources_vpc_config = {
    subnet_ids = ["subnet-xxxx", "subnet-yyyy"]
  }
}

resource "awscc_eks_cluster" "fail2" {
  name     = "example-cluster"
  role_arn = awscc_iam_role.main.arn

  resources_vpc_config = {
    subnet_ids             = ["subnet-xxxx", "subnet-yyyy"]
    endpoint_public_access = true
  }
}

