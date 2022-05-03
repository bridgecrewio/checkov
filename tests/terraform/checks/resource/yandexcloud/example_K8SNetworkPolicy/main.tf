# pass
resource "yandex_kubernetes_cluster" "pass" {
  name = "test-cluster"
  network_policy_provider = "CALICO"
}

# fail
resource "yandex_kubernetes_cluster" "fail" {
  name = "test-cluster"
}