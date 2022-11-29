module "log_group_external" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
  version = "2.1.0"
}
