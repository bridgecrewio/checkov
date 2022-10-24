resource "aws_elasticache_security_group" "exists" {
  name                 = "elasticache-security-group"
  security_group_names = [aws_security_group.bar.name]
}

resource "aws_security_group" "bar" {
  name = "security-group"
}