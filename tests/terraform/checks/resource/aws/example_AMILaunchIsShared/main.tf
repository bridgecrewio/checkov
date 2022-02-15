resource "aws_ami_launch_permission" "fail" {
  image_id   = "ami-2345678"
  account_id = "987654321"
}