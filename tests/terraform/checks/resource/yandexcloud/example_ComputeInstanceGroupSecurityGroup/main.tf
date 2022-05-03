# pass
resource "yandex_compute_instance_group" "pass" {
  name                = "test-ig"
  instance_template {
    platform_id = "standard-v1"

    network_interface {
      security_group_ids = [yandex_vpc_security_group.ssh-broker.id]
    }
  }
}

# fail
resource "yandex_compute_instance_group" "fail" {
  name                = "test-ig"
  instance_template {
    platform_id = "standard-v1"

    network_interface {
    }
  }
}

