# pass

# EC2 instance

resource "yandex_compute_instance" "default" {
  
}

resource "yandex_compute_instance" "private" {
  network_interface {
    nat = false
  }
}



# fail

# EC2 instance

resource "yandex_compute_instance" "public" {
  network_interface {
    nat = true
  }
}

