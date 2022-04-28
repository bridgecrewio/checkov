# pass
resource "yandex_compute_instance" "pass" {
  name = "test-vm"
  network_interface {
    security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
  }
}

# fail
resource "yandex_compute_instance" "fail" {
  name = "test-vm"
}