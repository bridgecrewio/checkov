resource "aws_instance" "some_instance" {
  ami = "some_ami"
  instance_type = "t3.nano"
  tags = {
    Name = "acme-machine"
  }
}

resource "aws_subnet" "acme_subnet" {
  cidr_block = ""
  vpc_id = ""

  tags = {
    acme = "true"
    Name = "notacme-subnet"
  }
}

resource "aws_s3_bucket" "acme_s3_bucket" {
  bucket = "acme-123456"
  tags = {
    Environment = "dev"
  }
}