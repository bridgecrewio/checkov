# pass

resource "aws_instance" "flag_enabled" {
  ami           = "ami-12345678"
  instance_type = "m3.xlarge"
  ebs_optimized = true
}

resource "aws_instance" "graviton_default" {
  ami           = "ami-12345678"
  instance_type = "t4g.micro"
}

resource "aws_instance" "nitro_default" {
  ami           = "ami-12345678"
  instance_type = "m5.large"
}

resource "aws_instance" "nitro_flag_disabled" {
  ami           = "ami-12345678"
  instance_type = "c7g.medium"
  ebs_optimized = false
}

# fail

resource "aws_instance" "no_type" {
  ami = "ami-12345678"
}

resource "aws_instance" "previous_generation" {
  ami           = "ami-12345678"
  instance_type = "m3.xlarge"
}

resource "aws_instance" "previous_generation_disabled" {
  ami           = "ami-12345678"
  instance_type = "c3.2xlarge"
  ebs_optimized = false
}

resource "aws_instance" "not_supported" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

resource "aws_instance" "unknown_type" {
  ami           = "ami-12345678"
  instance_type = var.instance_type
}

variable "instance_type" {
  type = string
}
