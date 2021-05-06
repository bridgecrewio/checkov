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

resource "aws_eip" "ok_eip_assoc" {
  vpc = true
}
