resource "aws_db_security_group" "exists" {
  name = "rds_sg"

  ingress {
    cidr = "10.0.0.0/24"
  }
}