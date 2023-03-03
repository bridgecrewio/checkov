module "pass" {
  source = "terraform-aws-modules/ec2-instance/aws"

  name = "terraform"

  ami                    = "ami-0ff8a91507f77f867"
  instance_type          = "t3.micro"
  key_name               = "user1"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-123456"
}

module "fail" {
  source = "cloudposse/ec2-instance/aws"

  name = "cloudposse"

  ami                    = "ami-0ff8a91507f77f867"
  ssh_key_pair           = "user1"
  instance_type          = "t3.micro"
  security_groups        = ["sg-12345678"]
  subnet                 = "subnet-123456"
  namespace              = "eg"
  stage                  = "dev"
}
