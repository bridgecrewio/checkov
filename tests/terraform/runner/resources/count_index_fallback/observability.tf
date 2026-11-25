resource "kubernetes_deployment_v1" "target" {
  count = var.target_enabled ? 1 : 0
  metadata {
    name      = "target"
    namespace = "monitoring"
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "target" }
    }
    template {
      metadata {
        labels = { app = "target" }
      }
      spec {
        container {
          name              = "target"
          image             = var.target_image
          image_pull_policy = "Always"
          resources {
            requests = { cpu = "10m", memory = "32Mi" }
            limits   = { cpu = "100m", memory = "64Mi" }
          }
          liveness_probe {
            http_get {
              path = "/metrics"
              port = 9121
            }
          }
          readiness_probe {
            http_get {
              path = "/metrics"
              port = 9121
            }
          }
          security_context {
            read_only_root_filesystem = true
            capabilities {
              drop = ["ALL"]
            }
          }
        }
      }
    }
  }
}
