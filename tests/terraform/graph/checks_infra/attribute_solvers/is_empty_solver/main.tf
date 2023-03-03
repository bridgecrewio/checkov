resource "aws_security_group" "aws_security_group_public" {
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 0
    protocol = ""
    to_port = 0
  }
}

resource "aws_security_group" "sg2" {
  ingress {
    from_port = "5432"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    self = "false"
    to_port = "1234"
  }
}

resource "aws_security_group" "sg3" {
  ingress {
    from_port = "5432"
    protocol = ""
    cidr_blocks = []
    self = "false"
    to_port = "1234"
  }
}
