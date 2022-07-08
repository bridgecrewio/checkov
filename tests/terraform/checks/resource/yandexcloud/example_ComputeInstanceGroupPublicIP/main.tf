# default
resource "yandex_compute_instance_group" "default" {
  name                = "test-ig"
  instance_template {
    platform_id = "standard-v1"

    network_interface {

    }
  }
}

# private
resource "yandex_compute_instance_group" "private" {
  name                = "test-ig"
  instance_template {
    platform_id = "standard-v1"

    network_interface {
      nat = false
    }
  }
}

# public
resource "yandex_compute_instance_group" "public" {
  name                = "test-ig"
  instance_template {
    platform_id = "standard-v1"

    network_interface {
      nat = true
    }
  }
}

