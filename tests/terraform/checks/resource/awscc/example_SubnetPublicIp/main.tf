resource "awscc_ec2_subnet" "fail" {
  vpc_id     = awscc_ec2_vpc.main.id
  cidr_block = "10.0.1.0/24"

  map_public_ip_on_launch = true
}
resource "awscc_ec2_subnet" "pass" {
  vpc_id     = awscc_ec2_vpc.main.id
  cidr_block = "10.0.1.0/24"

}

resource "awscc_ec2_subnet" "pass2" {
  vpc_id     = awscc_ec2_vpc.main.id
  cidr_block = "10.0.1.0/24"

  map_public_ip_on_launch = false
}
