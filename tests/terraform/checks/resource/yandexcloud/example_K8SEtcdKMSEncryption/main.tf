# pass
resource "yandex_kubernetes_cluster" "pass" {
  name = "test-cluster"
  kms_provider {
    key_id = "${yandex_kms_symmetric_key.kms_key_resource_name.id}"
  }
}

# fail
resource "yandex_kubernetes_cluster" "fail" {
  name = "test-cluster"
}