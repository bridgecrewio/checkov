# private

resource "yandex_kubernetes_node_group" "private" {
  name = "test-nodegroup"
  instance_template {
    network_interface {
      nat = false
    }
  }
}

# default

resource "yandex_kubernetes_node_group" "default" {
  name = "test-nodegroup"
  instance_template {
    network_interface {
      
    }
  }
}

# public

resource "yandex_kubernetes_node_group" "public" {
  name = "test-nodegroup"
  instance_template {
    network_interface {
      nat = true
    }
  }
}

