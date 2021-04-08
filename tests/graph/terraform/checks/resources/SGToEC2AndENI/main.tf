resource "aws_network_interface" "test" {
  subnet_id       = "aws_subnet.public_a.id"
  security_groups = [aws_security_group.ok_sg.id]
}

resource "aws_instance" "test" {
  ami           = "data.aws_ami.ubuntu.id"
  instance_type = "t3.micro"
  security_groups = [aws_security_group.ok_sg.id]
}

resource "aws_security_group" "ok_sg" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_security_group" "not_ok_sg" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
  }
}