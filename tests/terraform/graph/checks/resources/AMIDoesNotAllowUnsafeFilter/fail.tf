data "aws_ami" "example_fail" {
  most_recent = true
  name_regex  = "^ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
  owners      = ["099720109477"] # Canonical
  allow_unsafe_filter = true

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
