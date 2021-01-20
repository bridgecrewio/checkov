module "security_group1" {
  source  = "https://fakecreds:fakecreds@github.com/bridgecrewio/nonexistant_sample_repo.git"
  version = "latest"

  name        = "example"
  description = "Security group for example usage with EC2 instance"
  vpc_id      = data.aws_vpc.default.id

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["http-80-tcp", "all-icmp"]
  egress_rules        = ["all-all"]
}


module "security_group2" {
  source  = "https://fakecreds:fakecreds@github.com/bridgecrewio/nonexistantsamplerepo2.git"
  version = "latest"

  name        = "example"
  description = "Security group for example usage with EC2 instance"
  vpc_id      = data.aws_vpc.default.id

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["http-80-tcp", "all-icmp"]
  egress_rules        = ["all-all"]
}



