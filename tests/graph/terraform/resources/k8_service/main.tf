locals {
  name            = "bazel-remote-cache"
  namespace       = var.namespace
  cache_directory = "/var/cache/bazel-remote-cache"

  labels = {
    "app.kubernetes.io/name"       = local.name
    "app.kubernetes.io/instance"   = "web-server"
    "app.kubernetes.io/version"    = "1.0.0"
    "app.kubernetes.io/part-of"    = "foundation-infrastructure"
    "app.kubernetes.io/managed-by" = "terraform"
  }
}

resource "kubernetes_deployment" "bazel_remote_cache" {
  metadata {
    name      = local.name
    namespace = local.namespace
    labels    = local.labels

    annotations = {
      "reloader.stakater.com/auto" = "true"
    }
  }

  spec {
    replicas               = var.replicas
    revision_history_limit = 2

    strategy {
      type = "RollingUpdate"

      rolling_update {
        max_unavailable = 1
        max_surge       = 1
      }
    }

    selector {
      match_labels = local.labels
    }

    template {
      metadata {
        name      = local.name
        namespace = local.namespace
        labels    = local.labels

        annotations = {
          "iam.amazonaws.com/role" = var.iam_role
        }
      }

      spec {
        termination_grace_period_seconds = 10

        container {
          name              = local.name
          image             = "776709147254.dkr.ecr.us-west-2.amazonaws.com/bazel-remote-cache@sha256:5c7691bf88ee95f6b50953ac58a75db89340fd6d2636c8ca88e785e1e02790fc"
          image_pull_policy = "Always"

          args = ["--config_file=/etc/config.yaml"]

          port {
            container_port = 8080
          }

          port {
            container_port = 9092
          }

          volume_mount {
            mount_path = "/etc/config.yaml"
            name       = "bazel-remote-cache-config"
            sub_path   = "config.yaml"
            read_only  = true
          }

          volume_mount {
            name       = "bazel-remote-cache-data"
            mount_path = local.cache_directory
            sub_path   = "bazel-remote-cache-data"
            read_only  = false
          }

          resources {
            requests {
              memory = "4Gi"
              cpu    = "2"
            }

            limits {
              memory = "4Gi"
              cpu    = "2"
            }
          }

          liveness_probe {
            http_get {
              path = "/status"
              port = 8080
            }

            period_seconds        = 10
            success_threshold     = 1
            failure_threshold     = 2
            initial_delay_seconds = 120
          }

          readiness_probe {
            http_get {
              path = "/status"
              port = 8080
            }

            period_seconds    = 10
            success_threshold = 1
            failure_threshold = 2
          }
        }

        volume {
          name = "bazel-remote-cache-data"
          empty_dir {}
        }

        volume {
          name = "bazel-remote-cache-config"
          config_map {
            name = local.name
          }
        }

        affinity {
          pod_anti_affinity {
            preferred_during_scheduling_ignored_during_execution {
              weight = 50

              pod_affinity_term {
                topology_key = "domain.beta.kubernetes.io/zone"

                label_selector {
                  match_labels = local.labels
                }
              }
            }

            # Require pods to not schedule on the same node as to not use
            # the same local storate space
            required_during_scheduling_ignored_during_execution {
              topology_key = "kubernetes.io/hostname"
              label_selector {
                match_labels = local.labels
              }
            }

          }
        }
      }
    }
  }
}
