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

  egress {
    action              = "DROP"
    address_template_id = tencentcloud_address_template.foo.id
    description         = "B:Allow template"
  }

}
# failed
resource "tencentcloud_security_group_rule_set" "negative" {
  security_group_id = tencentcloud_security_group.base.id

  ingress {
    action     = "ACCEPT"
    cidr_block = "0.0.0.0/0"
    protocol   = "ALL"
    port       = "ALL"
  }

  egress {
    action                 = "DROP"
    address_template_group = tencentcloud_address_template_group.foo.id
    description            = "C:DROP template group"
  }
}