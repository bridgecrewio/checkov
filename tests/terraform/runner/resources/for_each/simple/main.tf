resource "aws_s3_bucket_object" "this_file" {
  source   = "readme.md"
}

resource "aws_instance" "public_server" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t2.micro"
  associate_public_ip_address = true
}