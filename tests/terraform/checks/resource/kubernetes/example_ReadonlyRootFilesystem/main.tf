
resource "kubernetes_pod" "fail_container" {
  metadata {
    name = "terraform-example"
  }

  spec {
    container = [
      {
        image = "nginx:1.7.9"
        name  = "example22"

        security_context = {
          privileged = true
        }

        env = {
          name  = "environment"
          value = "test"
        }

        port = {
          container_port = 8080
        }

        liveness_probe = {
          http_get = {
            path = "/nginx_status"
            port = 80

            http_header = {
              name  = "X-Custom-Header"
              value = "Awesome"
            }
          }

          initial_delay_seconds = 3
          period_seconds        = 3
        }
      }
      ,
      {
        image = "nginx:1.7.9"
        name  = "example22222"

        security_context = {
          privileged = true
        }

        env = {
          name  = "environment"
          value = "test"
        }

        port = {
          container_port = 8080
        }

        liveness_probe = {
          http_get = {
            path = "/nginx_status"
            port = 80

            http_header = {
              name  = "X-Custom-Header"
              value = "Awesome"
            }
          }

          initial_delay_seconds = 3
          period_seconds        = 3
        }
      }
    ]


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

resource "kubernetes_pod_v1" "fail_container" {
  metadata {
    name = "terraform-example"
  }

  spec {
    container = [
      {
        image = "nginx:1.7.9"
        name  = "example22"

        security_context = {
          privileged = true
        }

        env = {
          name  = "environment"
          value = "test"
        }

        port = {
          container_port = 8080
        }

        liveness_probe = {
          http_get = {
            path = "/nginx_status"
            port = 80

            http_header = {
              name  = "X-Custom-Header"
              value = "Awesome"
            }
          }

          initial_delay_seconds = 3
          period_seconds        = 3
        }
      }
    ,
      {
        image = "nginx:1.7.9"
        name  = "example22222"

        security_context = {
          privileged = true
        }

        env = {
          name  = "environment"
          value = "test"
        }

        port = {
          container_port = 8080
        }

        liveness_probe = {
          http_get = {
            path = "/nginx_status"
            port = 80

            http_header = {
              name  = "X-Custom-Header"
              value = "Awesome"
            }
          }

          initial_delay_seconds = 3
          period_seconds        = 3
        }
      }
    ]


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

resource "kubernetes_deployment" "fail_container" {
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
        container = [
          {
            image = "nginx:1.7.9"
            name  = "example22"

            security_context = {
              privileged = true
            }

            env = {
              name  = "environment"
              value = "test"
            }

            port = {
              container_port = 8080
            }

            liveness_probe = {
              http_get = {
                path = "/nginx_status"
                port = 80

                http_header = {
                  name  = "X-Custom-Header"
                  value = "Awesome"
                }
              }

              initial_delay_seconds = 3
              period_seconds        = 3
            }
          },
          {
            image = "nginx:1.7.9"
            name  = "example22222"

            security_context = {
              privileged = true
            }

            env = {
              name  = "environment"
              value = "test"
            }

            port = {
              container_port = 8080
            }

            liveness_probe = {
              http_get = {
                path = "/nginx_status"
                port = 80

                http_header = {
                  name  = "X-Custom-Header"
                  value = "Awesome"
                }
              }

              initial_delay_seconds = 3
              period_seconds        = 3
            }
          }
        ]


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

resource "kubernetes_deployment_v1" "fail_container" {
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
        container = [
          {
            image = "nginx:1.7.9"
            name  = "example22"

            security_context = {
              privileged = true
            }

            env = {
              name  = "environment"
              value = "test"
            }

            port = {
              container_port = 8080
            }

            liveness_probe = {
              http_get = {
                path = "/nginx_status"
                port = 80

                http_header = {
                  name  = "X-Custom-Header"
                  value = "Awesome"
                }
              }

              initial_delay_seconds = 3
              period_seconds        = 3
            }
          },
          {
            image = "nginx:1.7.9"
            name  = "example22222"

            security_context = {
              privileged = true
            }

            env = {
              name  = "environment"
              value = "test"
            }

            port = {
              container_port = 8080
            }

            liveness_probe = {
              http_get = {
                path = "/nginx_status"
                port = 80

                http_header = {
                  name  = "X-Custom-Header"
                  value = "Awesome"
                }
              }

              initial_delay_seconds = 3
              period_seconds        = 3
            }
          }
        ]


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

#missing
resource "kubernetes_pod" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    container {
      image = "nginx:1.7.9"
      name  = "example22"

      security_context {
        privileged = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

    container {
      image = "nginx:1.7.9"
      name  = "example22222"

      security_context {
        privileged = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

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

#missing
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
        container {
          image = "nginx:1.7.9"
          name  = "example22"

          security_context {
            privileged = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

        container {
          image = "nginx:1.7.9"
          name  = "example22222"

          security_context {
            privileged = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

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

#missing
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
        container {
          image = "nginx:1.7.9"
          name  = "example22"

          security_context {
            privileged = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

        container {
          image = "nginx:1.7.9"
          name  = "example22222"

          security_context {
            privileged = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

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

resource "kubernetes_pod_v1" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    container {
      image = "nginx:1.7.9"
      name  = "example22"

      security_context {
        privileged = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

    container {
      image = "nginx:1.7.9"
      name  = "example22222"

      security_context {
        privileged = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

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

#false
resource "kubernetes_pod" "fail2" {
  metadata {
    name = "terraform-example"
  }

  spec {
    container {
      image = "nginx:1.7.9"
      name  = "example22"

      security_context {
        privileged = false
        read_only_root_filesystem = false
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }
    container {
      image = "nginx:1.7.9"
      name  = "example22222"

      security_context {
        privileged = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

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

#false
resource "kubernetes_pod_v1" "fail2" {
  metadata {
    name = "terraform-example"
  }

  spec {
    container {
      image = "nginx:1.7.9"
      name  = "example22"

      security_context {
        privileged = false
        read_only_root_filesystem = false
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }
    container {
      image = "nginx:1.7.9"
      name  = "example22222"

      security_context {
        privileged = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

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

#false
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
        container {
          image = "nginx:1.7.9"
          name  = "example22"

          security_context {
            privileged                = false
            read_only_root_filesystem = false
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }
        container {
          image = "nginx:1.7.9"
          name  = "example22222"

          security_context {
            privileged = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

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

#false
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
        container {
          image = "nginx:1.7.9"
          name  = "example22"

          security_context {
            privileged                = false
            read_only_root_filesystem = false
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }
        container {
          image = "nginx:1.7.9"
          name  = "example22222"

          security_context {
            privileged = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

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
    container {
      image = "nginx:1.7.9"
      name  = "example22"

      security_context {
        privileged = false
        read_only_root_filesystem = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

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
    container {
      image = "nginx:1.7.9"
      name  = "example22"

      security_context {
        privileged = false
        read_only_root_filesystem = true
      }

      env {
        name  = "environment"
        value = "test"
      }

      port {
        container_port = 8080
      }

      liveness_probe {
        http_get {
          path = "/nginx_status"
          port = 80

          http_header {
            name  = "X-Custom-Header"
            value = "Awesome"
          }
        }

        initial_delay_seconds = 3
        period_seconds        = 3
      }
    }

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
        container {
          image = "nginx:1.7.9"
          name  = "example22"

          security_context {
            privileged                = false
            read_only_root_filesystem = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

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
        container {
          image = "nginx:1.7.9"
          name  = "example22"

          security_context {
            privileged                = false
            read_only_root_filesystem = true
          }

          env {
            name  = "environment"
            value = "test"
          }

          port {
            container_port = 8080
          }

          liveness_probe {
            http_get {
              path = "/nginx_status"
              port = 80

              http_header {
                name  = "X-Custom-Header"
                value = "Awesome"
              }
            }

            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }

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

