resource "aws_vpc" "my_vpc" {
  cidr_block = "172.16.0.0/16"

  tags = {
    Name = "tf-example"
  }
}

resource "aws_subnet" "my_subnet" {
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = "172.16.10.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "tf-example"
  }
}

# pass

resource "aws_network_interface" "pass_instance_network" {
  subnet_id   = aws_subnet.my_subnet.id
  private_ips = ["172.16.10.100"]

  tags = {
    Name = "primary_network_interface"
  }
}

resource "aws_instance" "pass_instance_network" {
  ami           = "ami-005e54dee72cc1d00"
  instance_type = "t2.micro"

  network_interface {
    network_interface_id = aws_network_interface.pass_instance_network.id
    device_index         = 0
  }
}

resource "aws_instance" "pass_instance_subnet" {
  ami           = "ami-005e54dee72cc1d00"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.my_subnet.id
}

resource "aws_network_interface" "pass_attachment" {
  subnet_id   = aws_subnet.my_subnet.id
  private_ips = ["172.16.10.100"]
}

resource "aws_instance" "pass_attachment" {
  ami           = "ami-005e54dee72cc1d00"
  instance_type = "t3.micro"
}

resource "aws_network_interface_attachment" "pass_attachment" {
  instance_id          = aws_instance.pass_attachment.id
  network_interface_id = aws_network_interface.pass_attachment.id
  device_index         = 0
}

# fail

resource "aws_instance" "fail" {
  ami           = "ami-005e54dee72cc1d00" # us-west-2
  instance_type = "t2.micro"
}