# pass
resource "yandex_kubernetes_node_group" "pass" {
  name        = "test-cluster"
  instance_template {
    network_interface {
      security_group_ids = [yandex_vpc_security_group.sg-ssh.id]
    }
  }
}

# fail
resource "yandex_kubernetes_node_group" "fail" {
  name        = "test-cluster"
}