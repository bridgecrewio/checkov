resource "aws_network_acl_rule" "fail" {
   egress         = false
   protocol       = "all"
   rule_action    = "allow"
   cidr_block     = "0.0.0.0/0"
   network_acl_id = aws_network_acl.bar.id
   rule_number    = 200
 }

resource "aws_network_acl" "bar" {
  vpc_id = "vpc-06074a092930bc809"
}

resource "aws_network_acl_rule" "pass" {
   egress         = false
   protocol       = "all"
   rule_action    = "allow"
   cidr_block     = "0.0.0.0/0"
   from_port = 80
   to_port = 80
   network_acl_id = aws_network_acl.bar.id
   rule_number    = 200
 }

resource "aws_network_acl_rule" "ignore" {
   egress         = true
   protocol       = "all"
   rule_action    = "allow"
   cidr_block     = "0.0.0.0/0"
   network_acl_id = aws_network_acl.bar.id
   rule_number    = 201
 }

resource "aws_network_acl_rule" "fail2" {
   egress         = false
   protocol       = "all"
   rule_action    = "allow"
   cidr_block     = "0.0.0.0/0"
   from_port=""
   network_acl_id = aws_network_acl.bar.id
   rule_number    = 201
 }