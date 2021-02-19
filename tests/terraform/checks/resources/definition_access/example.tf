locals {
  not_relevant = "nope"
}

variable "not_relevant_var" {
  type = string
  default = "nope"
}

resource "aws_s3_bucket" "foo" {
  bucket = "foo-bucket"
}
resource "aws_s3_bucket" "bar" {
  bucket = "bar-bucket"
}


resource "aws_instance" "foo" {
  ami = "ami-0123456789"
}