resource "aws_eip" "ok_eip" {
  instance = aws_instance.ec2.id
  vpc      = true
}

resource "aws_instance" "ec2" {
  ami               = "ami-21f78e11"
  availability_zone = "us-west-2a"
  instance_type     = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}

resource "aws_eip" "not_ok_eip" {
  vpc                       = true
  network_interface         = aws_network_interface.multi-ip.id
  associate_with_private_ip = "10.0.0.10"
}

# eip with domain attribute

resource "aws_eip" "ok_eip_domain" {
  instance = aws_instance.ok_eip_domain.id
  domain   = "vpc"
}

resource "aws_instance" "ok_eip_domain" {
  ami               = "ami-21f78e11"
  availability_zone = "us-west-2a"
  instance_type     = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}

# via aws_eip_association

resource "aws_eip_association" "eip_assoc" {
  instance_id   = aws_instance.ec2_assoc.id
  allocation_id = aws_eip.ok_eip_assoc.id
}

resource "aws_instance" "ec2_assoc" {
  ami               = "ami-21f78e11"
  availability_zone = "us-west-2a"
  instance_type     = "t2.micro"

  tags = {
    Name = "Assoc"
  }
}

resource "aws_eip" "ok_eip_domain_assoc" {
  domain = "vpc"
}

resource "aws_eip_association" "eip_domain_assoc" {
  instance_id   = aws_instance.ec_domain2_assoc.id
  allocation_id = aws_eip.ok_eip_domain_assoc.id
}

resource "aws_instance" "ec_domain2_assoc" {
  ami               = "ami-21f78e11"
  availability_zone = "us-west-2a"
  instance_type     = "t2.micro"

  tags = {
    Name = "Assoc"
  }
}

resource "aws_eip" "ok_eip_assoc" {
  vpc = true
}

# via aws_nat_gateway

resource "aws_eip" "ok_eip_nat" {
  vpc = true
}

resource "aws_nat_gateway" "ok_eip_nat" {
  allocation_id = aws_eip.ok_eip_nat.id
  subnet_id     = "aws_subnet.public.id"
}

resource "aws_transfer_server" "transfer_server_vpc" {
  count                        = local.count
  identity_provider_type       = "SERVICE_MANAGED"
  endpoint_type                = "VPC"

  endpoint_details {
    address_allocation_ids     = aws_eip.eip_ok_transer_server.*.id[count.index]
  }
}

resource "aws_eip" "eip_ok_transer_server" {
  count = local.count
  vpc   = true
}

resource "aws_eip" "ok_eip_module" {
  count    = 1
  instance = module.example[count.index].instance_id
  vpc      = true
}

resource "aws_eip" "ok_eip_data" {
  instance = data.aws_instance.id
  vpc      = true
}
