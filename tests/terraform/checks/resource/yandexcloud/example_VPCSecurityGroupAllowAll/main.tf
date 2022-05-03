# pass
resource "yandex_vpc_security_group" "pass-1" {
  name        = "My security group"
  ingress {
    v4_cidr_blocks = ["10.0.1.0/24", "10.0.2.0/24"]
    port           = 8080
  }
}

resource "yandex_vpc_security_group" "pass-2" {
  name        = "My security group"
  ingress {
    v4_cidr_blocks = ["0.0.0.0/0"]
    port           = 22
  }
}

# fail
resource "yandex_vpc_security_group" "fail-1" {
  name        = "My security group"
  ingress {
    v4_cidr_blocks = ["0.0.0.0/0"]
    from_port      = 0
    to_port        = 65535
  }
}

resource "yandex_vpc_security_group" "fail-2" {
  name        = "My security group"
  ingress {
    v4_cidr_blocks = ["10.0.0.0/24","0.0.0.0/0"]
  }
}