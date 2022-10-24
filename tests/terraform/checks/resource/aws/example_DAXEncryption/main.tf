# pass

resource "aws_dax_cluster" "enabled" {
  cluster_name       = "example"
  iam_role_arn       = "data.aws_iam_role.example.arn"
  node_type          = "dax.r4.large"
  replication_factor = 1

  server_side_encryption {
    enabled = True
  }
}

# fail

resource "aws_dax_cluster" "default" {
  cluster_name       = "example"
  iam_role_arn       = "data.aws_iam_role.example.arn"
  node_type          = "dax.r4.large"
  replication_factor = 1
}

resource "aws_dax_cluster" "disabled" {
  cluster_name       = "example"
  iam_role_arn       = "data.aws_iam_role.example.arn"
  node_type          = "dax.r4.large"
  replication_factor = 1

  server_side_encryption {
    enabled = False
  }
}
