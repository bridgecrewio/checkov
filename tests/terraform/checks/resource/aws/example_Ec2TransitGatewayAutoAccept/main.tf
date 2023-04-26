resource "aws_ec2_transit_gateway" "pass" {
  description = "pike"
}

resource "aws_ec2_transit_gateway" "pass2" {
  description = "sato"
  auto_accept_shared_attachments = "disable"
}

resource "aws_ec2_transit_gateway" "fail" {
  description = "sato"
  auto_accept_shared_attachments = "enable"
}