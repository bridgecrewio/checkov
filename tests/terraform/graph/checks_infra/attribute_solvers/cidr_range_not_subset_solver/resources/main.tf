resource "test" "pass1" {
  cidr_value = "10.11.10.12/32"
}

resource "test" "pass2" {
  cidr_value = 10.11.10.12/32
}

resource "test" "pass3" {
  cidr_value = "10.0.0.0/16"
}

resource "test" "pass4" {
  cidr_value = "10.255.255.0/24"
}

resource "test" "fail1" {
  cidr_value = "192.169.1.0/32"
}

resource "test" "fail2" {
  cidr_value = "172.16.0.0/12"
}

resource "test" "fail3" {
  cidr_value = "10.0.0.0/6"
}

resource "test" "ipv6_pass1" {
  ipv6_cidr_value = "fd12:3456:789a::/48"
}

resource "test" "ipv6_pass2" {
  ipv6_cidr_value = "fcab::/64"
}

resource "test" "ipv6_fail1" {
  ipv6_cidr_value = "2001:db8::/32"
}

resource "test" "ipv6_fail2" {
  ipv6_cidr_value = "2001:0db8:1234::/48"
}

resource "test" "ipv6_unknown1" {
  ipv6_cidr_value = "foo"
}
