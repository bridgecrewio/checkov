resource "aws_vpc" "my_vpc" {
  cidr_block = "172.16.0.0/16"

  tags = {
    Name = "tf-example"
    Env = "prod"
  }
}

resource "aws_subnet" "my_subnet" {
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = "172.16.10.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "tf-example"
    Env = "prod"
  }
}

resource "aws_network_interface" "network_interface_foo" {
  subnet_id   = aws_subnet.my_subnet.id
  private_ips = ["172.16.10.100"]

  tags = {
    Name = "primary_network_interface"
    Env = "prod"
  }
}

resource "aws_network_interface" "network_interface_goo" {
  subnet_id   = aws_subnet.my_subnet.id
  private_ips = ["172.16.10.100"]

  tags = {
    Name = "secondary_network_interface"
    Env = "dev"
  }
}

resource "aws_instance" "instance_foo" {
  ami           = "ami-005e54dee72cc1d00" # us-west-2
  instance_type = "t2.micro"

  network_interface {
    network_interface_id = aws_network_interface.network_interface_foo.id
    device_index         = 0
  }

  credit_specification {
    cpu_credits = "unlimited"
  }
}

resource "aws_instance" "instance_bar" {
  ami           = "ami-005e54dee72cc1d00" # us-west-2
  instance_type = "t2.micro"

  credit_specification {
    cpu_credits = "unlimited"
  }

  tags = {
    Env = "prod"
  }
}

resource "aws_vpc" "other_vpc" {
  cidr_block = "124.16.0.0/16"

  tags = {
    Name = "not_connected"
  }
}