# pass
resource "yandex_vpc_security_group_rule" "pass-1" {
  direction              = "ingress"
  v4_cidr_blocks         = ["0.0.0.0/0"]
  from_port              = 8090
  to_port                = 8099
  protocol               = "UDP"
}

resource "yandex_vpc_security_group_rule" "pass-2" {
  security_group_binding = yandex_vpc_security_group.group1.id
  direction              = "ingress"
  v4_cidr_blocks         = ["10.0.1.0/24"]
  from_port              = 8090
  to_port                = 8099
  protocol               = "UDP"
}

resource "yandex_vpc_security_group_rule" "pass-3" {
  security_group_binding = yandex_vpc_security_group.group1.id
  direction              = "ingress"
  v4_cidr_blocks         = ["0.0.0.0/0"]
  port                   = 22
  protocol               = "TCP"
}

resource "yandex_vpc_security_group_rule" "pass-4" {
  security_group_binding = yandex_vpc_security_group.group1.id
  direction              = "egress"
  v4_cidr_blocks         = ["0.0.0.0/0"]
  from_port              = 0
  to_port                = 65535
  protocol               = "TCP"
}

# fail
resource "yandex_vpc_security_group_rule" "fail-1" {
  security_group_binding = yandex_vpc_security_group.group1.id
  direction              = "ingress"
  description            = "rule1 description"
  v4_cidr_blocks         = ["0.0.0.0/0"]
  from_port              = 0
  to_port                = 65535
  protocol               = "TCP"
}

resource "yandex_vpc_security_group_rule" "fail-2" {
  security_group_binding = yandex_vpc_security_group.group1.id
  direction              = "ingress"
  description            = "rule2 description"
  v4_cidr_blocks         = ["0.0.0.0/0"]
  protocol               = "TCP"
}

resource "yandex_vpc_security_group_rule" "fail-3" {
  security_group_binding = yandex_vpc_security_group.group1.id
  direction              = "ingress"
  v4_cidr_blocks         = ["10.0.0.0/24","0.0.0.0/0"]
  port                   = -1
  protocol               = "TCP"
}