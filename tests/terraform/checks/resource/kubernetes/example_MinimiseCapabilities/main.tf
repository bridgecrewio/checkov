
resource "kubernetes_pod" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true


    container {
      image             = "nginx"
      image_pull_policy = "Never"
      name              = "example"

      security_context {
        privileged                 = true
        allow_privilege_escalation = true
        capabilities {
          add  = ["NET_RAW"]
          drop = ["NET_BIND_SERVICE"]
        }
      }
      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
        host_port      = 8080
      }

      # resources = {
      #   requests = {
      #     memory = "50Mi"
      #   }
      #   limits ={
      #     memory = "50Mi"
      #   }
      # }
      # liveness_probe {
      #   http_get {
      #     path = "/nginx_status"
      #     port = 80

      #     http_header {
      #       name  = "X-Custom-Header"
      #       value = "Awesome"
      #     }
      #   }

      #   initial_delay_seconds = 3
      #   period_seconds        = 3
      # }
    }
    # readiness_probe {
    #     failure_threshold = 3
    #     http_get {
    #       path = "/health"
    #       port = "10254"
    #       scheme = "http"
    #     }
    #     period_seconds = 10
    #     success_threshold = 1
    #     timeout_seconds = 10
    #   }
    # }
    dns_config {
      nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
      searches    = ["example.com"]

      option {
        name  = "ndots"
        value = 1
      }

      option {
        name = "use-vc"
      }
    }

    dns_policy = "None"
  }
}

resource "kubernetes_pod_v1" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true


    container {
      image             = "nginx"
      image_pull_policy = "Never"
      name              = "example"

      security_context {
        privileged                 = true
        allow_privilege_escalation = true
        capabilities {
          add  = ["NET_RAW"]
          drop = ["NET_BIND_SERVICE"]
        }
      }
      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
        host_port      = 8080
      }

      # resources = {
      #   requests = {
      #     memory = "50Mi"
      #   }
      #   limits ={
      #     memory = "50Mi"
      #   }
      # }
      # liveness_probe {
      #   http_get {
      #     path = "/nginx_status"
      #     port = 80

      #     http_header {
      #       name  = "X-Custom-Header"
      #       value = "Awesome"
      #     }
      #   }

      #   initial_delay_seconds = 3
      #   period_seconds        = 3
      # }
    }
    # readiness_probe {
    #     failure_threshold = 3
    #     http_get {
    #       path = "/health"
    #       port = "10254"
    #       scheme = "http"
    #     }
    #     period_seconds = 10
    #     success_threshold = 1
    #     timeout_seconds = 10
    #   }
    # }
    dns_config {
      nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
      searches    = ["example.com"]

      option {
        name  = "ndots"
        value = 1
      }

      option {
        name = "use-vc"
      }
    }

    dns_policy = "None"
  }
}

resource "kubernetes_deployment" "fail" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        k8s-app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          k8s-app = "nginx"
        }
      }

      spec {
        host_ipc = true
        host_pid = true


        container {
          image             = "nginx"
          image_pull_policy = "Never"
          name              = "example"

          security_context {
            privileged                 = true
            allow_privilege_escalation = true
            capabilities {
              add  = ["NET_RAW"]
              drop = ["NET_BIND_SERVICE"]
            }
          }
          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
            host_port      = 8080
          }

          # resources = {
          #   requests = {
          #     memory = "50Mi"
          #   }
          #   limits ={
          #     memory = "50Mi"
          #   }
          # }
          # liveness_probe {
          #   http_get {
          #     path = "/nginx_status"
          #     port = 80

          #     http_header {
          #       name  = "X-Custom-Header"
          #       value = "Awesome"
          #     }
          #   }

          #   initial_delay_seconds = 3
          #   period_seconds        = 3
          # }
        }
        # readiness_probe {
        #     failure_threshold = 3
        #     http_get {
        #       path = "/health"
        #       port = "10254"
        #       scheme = "http"
        #     }
        #     period_seconds = 10
        #     success_threshold = 1
        #     timeout_seconds = 10
        #   }
        # }
        dns_config {
          nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
          searches    = ["example.com"]

          option {
            name  = "ndots"
            value = 1
          }

          option {
            name = "use-vc"
          }
        }

        dns_policy = "None"
      }
    }
  }
}

resource "kubernetes_deployment_v1" "fail" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        k8s-app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          k8s-app = "nginx"
        }
      }

      spec {
        host_ipc = true
        host_pid = true


        container {
          image             = "nginx"
          image_pull_policy = "Never"
          name              = "example"

          security_context {
            privileged                 = true
            allow_privilege_escalation = true
            capabilities {
              add  = ["NET_RAW"]
              drop = ["NET_BIND_SERVICE"]
            }
          }
          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
            host_port      = 8080
          }

          # resources = {
          #   requests = {
          #     memory = "50Mi"
          #   }
          #   limits ={
          #     memory = "50Mi"
          #   }
          # }
          # liveness_probe {
          #   http_get {
          #     path = "/nginx_status"
          #     port = 80

          #     http_header {
          #       name  = "X-Custom-Header"
          #       value = "Awesome"
          #     }
          #   }

          #   initial_delay_seconds = 3
          #   period_seconds        = 3
          # }
        }
        # readiness_probe {
        #     failure_threshold = 3
        #     http_get {
        #       path = "/health"
        #       port = "10254"
        #       scheme = "http"
        #     }
        #     period_seconds = 10
        #     success_threshold = 1
        #     timeout_seconds = 10
        #   }
        # }
        dns_config {
          nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
          searches    = ["example.com"]

          option {
            name  = "ndots"
            value = 1
          }

          option {
            name = "use-vc"
          }
        }

        dns_policy = "None"
      }
    }
  }
}

resource "kubernetes_pod" "fail2" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true


    container {
      image             = "nginx"
      image_pull_policy = "Never"
      name              = "example"

      security_context {
        privileged                 = true
        allow_privilege_escalation = true
        capabilities {
          add  = ["NET_RAW"]
        }
      }
      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
        host_port      = 8080
      }

      # resources = {
      #   requests = {
      #     memory = "50Mi"
      #   }
      #   limits ={
      #     memory = "50Mi"
      #   }
      # }
      # liveness_probe {
      #   http_get {
      #     path = "/nginx_status"
      #     port = 80

      #     http_header {
      #       name  = "X-Custom-Header"
      #       value = "Awesome"
      #     }
      #   }

      #   initial_delay_seconds = 3
      #   period_seconds        = 3
      # }
    }
    # readiness_probe {
    #     failure_threshold = 3
    #     http_get {
    #       path = "/health"
    #       port = "10254"
    #       scheme = "http"
    #     }
    #     period_seconds = 10
    #     success_threshold = 1
    #     timeout_seconds = 10
    #   }
    # }
    dns_config {
      nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
      searches    = ["example.com"]

      option {
        name  = "ndots"
        value = 1
      }

      option {
        name = "use-vc"
      }
    }

    dns_policy = "None"
  }
}

resource "kubernetes_pod_v1" "fail2" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true


    container {
      image             = "nginx"
      image_pull_policy = "Never"
      name              = "example"

      security_context {
        privileged                 = true
        allow_privilege_escalation = true
        capabilities {
          add  = ["NET_RAW"]
        }
      }
      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
        host_port      = 8080
      }

      # resources = {
      #   requests = {
      #     memory = "50Mi"
      #   }
      #   limits ={
      #     memory = "50Mi"
      #   }
      # }
      # liveness_probe {
      #   http_get {
      #     path = "/nginx_status"
      #     port = 80

      #     http_header {
      #       name  = "X-Custom-Header"
      #       value = "Awesome"
      #     }
      #   }

      #   initial_delay_seconds = 3
      #   period_seconds        = 3
      # }
    }
    # readiness_probe {
    #     failure_threshold = 3
    #     http_get {
    #       path = "/health"
    #       port = "10254"
    #       scheme = "http"
    #     }
    #     period_seconds = 10
    #     success_threshold = 1
    #     timeout_seconds = 10
    #   }
    # }
    dns_config {
      nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
      searches    = ["example.com"]

      option {
        name  = "ndots"
        value = 1
      }

      option {
        name = "use-vc"
      }
    }

    dns_policy = "None"
  }
}

resource "kubernetes_deployment" "fail2" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        k8s-app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          k8s-app = "nginx"
        }
      }

      spec {
        host_ipc = true
        host_pid = true


        container {
          image             = "nginx"
          image_pull_policy = "Never"
          name              = "example"

          security_context {
            privileged                 = true
            allow_privilege_escalation = true
            capabilities {
              add = ["NET_RAW"]
            }
          }
          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
            host_port      = 8080
          }

          # resources = {
          #   requests = {
          #     memory = "50Mi"
          #   }
          #   limits ={
          #     memory = "50Mi"
          #   }
          # }
          # liveness_probe {
          #   http_get {
          #     path = "/nginx_status"
          #     port = 80

          #     http_header {
          #       name  = "X-Custom-Header"
          #       value = "Awesome"
          #     }
          #   }

          #   initial_delay_seconds = 3
          #   period_seconds        = 3
          # }
        }
        # readiness_probe {
        #     failure_threshold = 3
        #     http_get {
        #       path = "/health"
        #       port = "10254"
        #       scheme = "http"
        #     }
        #     period_seconds = 10
        #     success_threshold = 1
        #     timeout_seconds = 10
        #   }
        # }
        dns_config {
          nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
          searches    = ["example.com"]

          option {
            name  = "ndots"
            value = 1
          }

          option {
            name = "use-vc"
          }
        }

        dns_policy = "None"
      }
    }
  }
}

resource "kubernetes_deployment_v1" "fail2" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        k8s-app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          k8s-app = "nginx"
        }
      }

      spec {
        host_ipc = true
        host_pid = true


        container {
          image             = "nginx"
          image_pull_policy = "Never"
          name              = "example"

          security_context {
            privileged                 = true
            allow_privilege_escalation = true
            capabilities {
              add = ["NET_RAW"]
            }
          }
          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
            host_port      = 8080
          }

          # resources = {
          #   requests = {
          #     memory = "50Mi"
          #   }
          #   limits ={
          #     memory = "50Mi"
          #   }
          # }
          # liveness_probe {
          #   http_get {
          #     path = "/nginx_status"
          #     port = 80

          #     http_header {
          #       name  = "X-Custom-Header"
          #       value = "Awesome"
          #     }
          #   }

          #   initial_delay_seconds = 3
          #   period_seconds        = 3
          # }
        }
        # readiness_probe {
        #     failure_threshold = 3
        #     http_get {
        #       path = "/health"
        #       port = "10254"
        #       scheme = "http"
        #     }
        #     period_seconds = 10
        #     success_threshold = 1
        #     timeout_seconds = 10
        #   }
        # }
        dns_config {
          nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
          searches    = ["example.com"]

          option {
            name  = "ndots"
            value = 1
          }

          option {
            name = "use-vc"
          }
        }

        dns_policy = "None"
      }
    }
  }
}

resource "kubernetes_pod" "pass" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true


    container {
      image             = "nginx"
      image_pull_policy = "Never"
      name              = "example"

      security_context {
        privileged                 = true
        allow_privilege_escalation = true
        capabilities {
          add  = ["NET_RAW"]
          drop = ["ALL"]
        }
      }
      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
        host_port      = 8080
      }

      # resources = {
      #   requests = {
      #     memory = "50Mi"
      #   }
      #   limits ={
      #     memory = "50Mi"
      #   }
      # }
      # liveness_probe {
      #   http_get {
      #     path = "/nginx_status"
      #     port = 80

      #     http_header {
      #       name  = "X-Custom-Header"
      #       value = "Awesome"
      #     }
      #   }

      #   initial_delay_seconds = 3
      #   period_seconds        = 3
      # }
    }
    # readiness_probe {
    #     failure_threshold = 3
    #     http_get {
    #       path = "/health"
    #       port = "10254"
    #       scheme = "http"
    #     }
    #     period_seconds = 10
    #     success_threshold = 1
    #     timeout_seconds = 10
    #   }
    # }
    dns_config {
      nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
      searches    = ["example.com"]

      option {
        name  = "ndots"
        value = 1
      }

      option {
        name = "use-vc"
      }
    }

    dns_policy = "None"
  }
}

resource "kubernetes_pod_v1" "pass" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true


    container {
      image             = "nginx"
      image_pull_policy = "Never"
      name              = "example"

      security_context {
        privileged                 = true
        allow_privilege_escalation = true
        capabilities {
          add  = ["NET_RAW"]
          drop = ["ALL"]
        }
      }
      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
        host_port      = 8080
      }

      # resources = {
      #   requests = {
      #     memory = "50Mi"
      #   }
      #   limits ={
      #     memory = "50Mi"
      #   }
      # }
      # liveness_probe {
      #   http_get {
      #     path = "/nginx_status"
      #     port = 80

      #     http_header {
      #       name  = "X-Custom-Header"
      #       value = "Awesome"
      #     }
      #   }

      #   initial_delay_seconds = 3
      #   period_seconds        = 3
      # }
    }
    # readiness_probe {
    #     failure_threshold = 3
    #     http_get {
    #       path = "/health"
    #       port = "10254"
    #       scheme = "http"
    #     }
    #     period_seconds = 10
    #     success_threshold = 1
    #     timeout_seconds = 10
    #   }
    # }
    dns_config {
      nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
      searches    = ["example.com"]

      option {
        name  = "ndots"
        value = 1
      }

      option {
        name = "use-vc"
      }
    }

    dns_policy = "None"
  }
}

resource "kubernetes_deployment" "pass" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        k8s-app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          k8s-app = "nginx"
        }
      }

      spec {
        host_ipc = true
        host_pid = true


        container {
          image             = "nginx"
          image_pull_policy = "Never"
          name              = "example"

          security_context {
            privileged                 = true
            allow_privilege_escalation = true
            capabilities {
              add  = ["NET_RAW"]
              drop = ["ALL"]
            }
          }
          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
            host_port      = 8080
          }

          # resources = {
          #   requests = {
          #     memory = "50Mi"
          #   }
          #   limits ={
          #     memory = "50Mi"
          #   }
          # }
          # liveness_probe {
          #   http_get {
          #     path = "/nginx_status"
          #     port = 80

          #     http_header {
          #       name  = "X-Custom-Header"
          #       value = "Awesome"
          #     }
          #   }

          #   initial_delay_seconds = 3
          #   period_seconds        = 3
          # }
        }
        # readiness_probe {
        #     failure_threshold = 3
        #     http_get {
        #       path = "/health"
        #       port = "10254"
        #       scheme = "http"
        #     }
        #     period_seconds = 10
        #     success_threshold = 1
        #     timeout_seconds = 10
        #   }
        # }
        dns_config {
          nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
          searches    = ["example.com"]

          option {
            name  = "ndots"
            value = 1
          }

          option {
            name = "use-vc"
          }
        }

        dns_policy = "None"
      }
    }
  }
}

resource "kubernetes_deployment_v1" "pass" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        k8s-app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          k8s-app = "nginx"
        }
      }

      spec {
        host_ipc = true
        host_pid = true


        container {
          image             = "nginx"
          image_pull_policy = "Never"
          name              = "example"

          security_context {
            privileged                 = true
            allow_privilege_escalation = true
            capabilities {
              add  = ["NET_RAW"]
              drop = ["ALL"]
            }
          }
          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
            host_port      = 8080
          }

          # resources = {
          #   requests = {
          #     memory = "50Mi"
          #   }
          #   limits ={
          #     memory = "50Mi"
          #   }
          # }
          # liveness_probe {
          #   http_get {
          #     path = "/nginx_status"
          #     port = 80

          #     http_header {
          #       name  = "X-Custom-Header"
          #       value = "Awesome"
          #     }
          #   }

          #   initial_delay_seconds = 3
          #   period_seconds        = 3
          # }
        }
        # readiness_probe {
        #     failure_threshold = 3
        #     http_get {
        #       path = "/health"
        #       port = "10254"
        #       scheme = "http"
        #     }
        #     period_seconds = 10
        #     success_threshold = 1
        #     timeout_seconds = 10
        #   }
        # }
        dns_config {
          nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
          searches    = ["example.com"]

          option {
            name  = "ndots"
            value = 1
          }

          option {
            name = "use-vc"
          }
        }

        dns_policy = "None"
      }
    }
  }
}
