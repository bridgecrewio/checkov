module "security_group" {
  source  = "git::https://github.com/terraform-aws-modules/terraform-aws-security-group.git"
  version = "~> 3.0"

  name        = "example"
  description = "Security group for example usage with EC2 instance"
  vpc_id      = data.aws_vpc.default.id

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["http-80-tcp", "all-icmp"]
  egress_rules        = ["all-all"]
}
