# pass

resource "yandex_kubernetes_cluster" "pass" {
  name = "test-cluster"
  master {
    maintenance_policy {
      auto_upgrade = true
    }
  }
}

# fail

resource "yandex_kubernetes_cluster" "fail" {
  name = "test-cluster"
  master {
    maintenance_policy {
      auto_upgrade = false
    }
  }
}

