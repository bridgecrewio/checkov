# pass
resource "tencentcloud_security_group_rule_set" "positive" {
  security_group_id = tencentcloud_security_group.base.id

  ingress {
    action      = "ACCEPT"
    cidr_block  = "10.0.0.0/22"
    protocol    = "TCP"
    port        = "80-90"
    description = "A:Allow Ips and 80-90"
  }

}
# failed
resource "tencentcloud_security_group_rule_set" "negative1" {
  security_group_id = tencentcloud_security_group.base.id

  ingress {
    action     = "ACCEPT"
    cidr_block = "0.0.0.0/0"
    protocol   = "ALL"
    port       = "ALL"
  }
}

resource "tencentcloud_security_group_rule_set" "negative2" {
  security_group_id = tencentcloud_security_group.base.id

  ingress {
    action          = "ACCEPT"
    ipv6_cidr_block = "::/0"
    protocol        = "ALL"
    port            = "ALL"
  }
}

resource "tencentcloud_security_group_rule_set" "negative3" {
  security_group_id = tencentcloud_security_group.base.id

  ingress {
    action          = "ACCEPT"
    ipv6_cidr_block = "0::0/0"
    protocol        = "ALL"
    port            = "ALL"
  }
}