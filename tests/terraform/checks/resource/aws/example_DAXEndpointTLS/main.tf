resource "aws_dax_cluster" "fail" {
  cluster_name                     = var.cluster_name
  iam_role_arn                     = var.iam_role_arn
  parameter_group_name             = aws_dax_parameter_group.example.name
  subnet_group_name                = aws_dax_subnet_group.example.name
  cluster_endpoint_encryption_type = "NONE"
  server_side_encryption {
    enabled = false #default is false
  }
  tags = { test = "Fail" }
}

resource "aws_dax_cluster" "fail2" {
  cluster_name         = var.cluster_name
  iam_role_arn         = var.iam_role_arn
  parameter_group_name = aws_dax_parameter_group.example.name
  subnet_group_name    = aws_dax_subnet_group.example.name
  tags                 = { test = "Fail" }
}

resource "aws_dax_cluster" "pass" {
  cluster_name                     = var.cluster_name
  iam_role_arn                     = var.iam_role_arn
  parameter_group_name             = aws_dax_parameter_group.example.name
  subnet_group_name                = aws_dax_subnet_group.example.name
  cluster_endpoint_encryption_type = "TLS"
  server_side_encryption {
    enabled = false #default is false
  }
  tags = { test = "Fail" }
}