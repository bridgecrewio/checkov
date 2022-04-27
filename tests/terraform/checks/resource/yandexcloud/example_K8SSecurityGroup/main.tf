# pass
resource "yandex_kubernetes_cluster" "pass" {
  name = "test-cluster"
  master {
    security_group_ids = [
      yandex_vpc_security_group.kube-sg-ssh.id
    ]
  }
}

# fail
resource "yandex_kubernetes_cluster" "fail" {
  name = "test-cluster"
}