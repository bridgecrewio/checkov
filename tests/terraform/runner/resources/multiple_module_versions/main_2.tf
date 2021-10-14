module "ec2_private_latest_2" {
  source = "terraform-aws-modules/ec2-instance/aws"

  name = "ec2-private-latest"

  ami                    = "ami-0ff8a91507f77f867"
  instance_type          = "t3.micro"
  key_name               = "user1"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-123456"

  associate_public_ip_address = false
}

module "ec2_public_latest_2" {
  source = "terraform-aws-modules/ec2-instance/aws"

  name = "ec2-public-latest"

  ami                    = "ami-0ff8a91507f77f867"
  instance_type          = "t3.micro"
  key_name               = "user1"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-123456"

  associate_public_ip_address = true
}

module "ec2_private_old_2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "2.21.0"

  name = "ec2-private-2.21.0"

  ami                    = "ami-0ff8a91507f77f867"
  instance_type          = "t3.micro"
  key_name               = "user1"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-123456"

  associate_public_ip_address = false
}

module "ec2_public_old_2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "2.21.0"

  name = "ec2-public-2.21.0"

  ami                    = "ami-0ff8a91507f77f867"
  instance_type          = "t3.micro"
  key_name               = "user1"
  vpc_security_group_ids = ["sg-12345678"]
  subnet_id              = "subnet-123456"

  associate_public_ip_address = true
}
