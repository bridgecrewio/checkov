resource "aws_security_group" "failed_cidr_blocks" {
  name        = "friendly_subnets"
  description = "Allows access from friendly subnets"
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = -1
    cidr_blocks = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
  }
}

resource "aws_security_group" "passed_cidr_block" {
  name        = "friendly_subnets"
  description = "Allows access from friendly subnets"
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = -1
    cidr_blocks = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
  }
}