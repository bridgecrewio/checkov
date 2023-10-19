module "log_group" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"

  name_prefix       = "my-log-group-"
  retention_in_days = 7
}

module "log_group_v4" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
  version = "~> 4.0"

  name_prefix       = "my-log-group-"
  retention_in_days = 7
}
