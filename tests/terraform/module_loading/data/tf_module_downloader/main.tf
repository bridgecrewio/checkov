module "local_module" {
  source = "../../../../../../../platform/src/stacks/accountStack"
  aws_profile = ""
  pgadmin_password = ""
  region = ""
  state_bucket = ""
}

module "remote_module" {
  source = "terraform-aws-modules/s3-bucket/aws"
  version = "2.1.0"
}
