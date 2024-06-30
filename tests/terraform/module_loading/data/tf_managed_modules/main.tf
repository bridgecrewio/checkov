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

#NOTE - THIS IS COMMENTED AS PART OF THE TEST TO CHECK HANDLING OF COMMENTED OUT MODULES. DO NOT DELETE
# Need to verify this type of comment is not an issue.
#module "log_group_pound_comment" {
#  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
#
#  name_prefix       = "my-log-group-"
#  retention_in_days = 7
#}


# Need to verify this type of comment is not an issue.
/*
module "log_group_star_comment" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
  name_prefix       = "my-log-group-"
  retention_in_days = 7
}
*/