# default

resource "yandex_compute_instance" "default" {
  name = "test-vm"
  platform-id = "standard-v3"
  zone = "ru-central1-a"
}

# pass

resource "yandex_compute_instance" "pass" {
  name = "test-vm"
  platform-id = "standard-v3"
  zone = "ru-central1-a"

  metadata = {
    serial-port-enable = 0
  }
}

# fail

resource "yandex_compute_instance" "fail" {
  name = "test-vm"
  platform-id = "standard-v3"
  zone = "ru-central1-a"

  metadata = {
    serial-port-enable = 1
  }
}