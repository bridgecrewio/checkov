resource "aws_vpc" "my_vpc" {
  cidr_block = "172.16.0.0/16"

  tags = {
    Name = "tf-example"
  }
}

resource "aws_subnet" "subnet_public_ip" {
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = "172.16.10.0/24"
  availability_zone = "us-west-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "first-tf-example"
  }
}

resource "aws_subnet" "subnet_not_public_ip" {
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = "172.16.10.0/24"
  availability_zone = "eu-central-1"

  tags = {
    Name = "second-tf-example"
  }
}


resource "aws_default_security_group" "default_security_group_open" {
  vpc_id = aws_vpc.my_vpc.id

  ingress {
    protocol  = -1
    self      = true
    from_port = 0
    to_port   = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_default_security_group" "default_security_group_closed" {
  vpc_id = aws_vpc.my_vpc.id

  ingress {
    protocol  = -1
    self      = true
    from_port = 0
    to_port   = 0
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "with_open_def_security_groups" {
  ami           = "ami-0"
  instance_type = "t2.micro"

  credit_specification {
    cpu_credits = "unlimited"
  }

  security_groups = [aws_default_security_group.default_security_group_open.id]
}

resource "aws_instance" "with_closed_def_security_groups" {
  ami           = "ami-1"
  instance_type = "t2.micro"

  credit_specification {
    cpu_credits = "unlimited"
  }

  security_groups = [aws_default_security_group.default_security_group_closed.id]
}


resource "aws_instance" "with_open_security_groups" {
  ami           = "ami-2"
  instance_type = "t2.micro"

  credit_specification {
    cpu_credits = "unlimited"
  }

  vpc_security_group_ids = [aws_security_group.allow_tls.id]
}

resource "aws_security_group" "allow_tls" {
  name        = "allow_tls"
  description = "Allow TLS inbound traffic"
  vpc_id      = aws_vpc.my_vpc.id

  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }


  tags = {
    Name = "allow_tls"
  }
}


resource "aws_instance" "with_subnet_public" {
  ami           = "ami-3"
  instance_type = "t2.micro"

  credit_specification {
    cpu_credits = "unlimited"
  }

  subnet_id = aws_subnet.subnet_public_ip.id
}

resource "aws_instance" "with_subnet_not_public" {
  ami           = "ami-4"
  instance_type = "t2.micro"

  credit_specification {
    cpu_credits = "unlimited"
  }

  subnet_id = aws_subnet.subnet_not_public_ip.id
}