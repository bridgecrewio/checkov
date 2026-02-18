resource "awscc_ec2_volume" "fail" {
  availability_zone = "us-west-2a"
  size              = 40
}

resource "awscc_ec2_volume" "pass" {
  availability_zone = "us-west-2a"
  size              = 40
  encrypted         = true
}
