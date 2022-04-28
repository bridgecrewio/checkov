# pass

resource "yandex_kubernetes_node_group" "pass" {
  name = "test-nodegroup"
  maintenance_policy {
    auto_upgrade = true
  }
}

# fail

resource "yandex_kubernetes_node_group" "fail" {
  name = "test-nodegroup"
  maintenance_policy {
    auto_upgrade = false
  }
}

