module "web_server_sg" {
  source  = "git::git@github.aig.net:terraform-modules/aws-cloudfront//s3-cdn?ref=develop"
  version = "4.0.0"

  name        = "web-server"
  description = "Security group for web-server with HTTP ports open within VPC"
  vpc_id      = "vpc-12345678"

  ingress_cidr_blocks = ["10.10.0.0/16"]
}