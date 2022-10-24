# private

resource "yandex_kubernetes_cluster" "private" {
  name = "test-cluster"
  master {
    public_ip = false
  }
}

# default

resource "yandex_kubernetes_cluster" "default" {
  name = "test-cluster"
}

# public

resource "yandex_kubernetes_cluster" "public" {
  name = "test-cluster"
  master {
    public_ip = true
  }
}

