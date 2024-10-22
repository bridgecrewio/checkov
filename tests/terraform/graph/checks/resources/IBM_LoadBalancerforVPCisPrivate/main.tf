variable "pud-subnet" {
  subnet = "192.168.20.0/24"
}

# Case 1: Pass: type = "private"

resource "ibm_is_lb" "pass" {
  name    = "pud-load-balancer"
  subnets = [var.pud-subnet]
  type = "private"
}

# Case 2: FAIL: 'type' does not exist. By default, type = 'public'

resource "ibm_is_lb" "fail" {
  name    = "pud-load-balancer"
  subnets = [var.pud-subnet]
  profile = "network-fixed"
}
