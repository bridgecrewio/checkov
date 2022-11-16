# fails no spec
resource "kubernetes_pod" "fail" {
  metadata {
    name = "terraform-example"
  }
}

# fails no spec
resource "kubernetes_pod_v1" "fail" {
  metadata {
    name = "terraform-example"
  }
}

# fails no spec
resource "kubernetes_deployment" "fail" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }
}

# fails no spec
resource "kubernetes_deployment_v1" "fail" {
  metadata {
    name = "terraform-example"
    labels = {
      k8s-app = "nginx"
    }
  }
}

#no capabilities
resource "kubernetes_pod" "fail4" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

      security_context {

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

#no capabilities
resource "kubernetes_pod_v1" "fail4" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

      security_context {

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

#no capabilities
resource "kubernetes_deployment" "fail4" {
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
          name  = "example"

          security_context {

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

#no capabilities
resource "kubernetes_deployment_v1" "fail4" {
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
          name  = "example"

          security_context {

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


#no context
resource "kubernetes_pod" "fail5" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

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

#no context
resource "kubernetes_pod_v1" "fail5" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

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

#no context
resource "kubernetes_deployment" "fail5" {
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
          name  = "example"

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

#no context
resource "kubernetes_deployment_v1" "fail5" {
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
          name  = "example"

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


#doesnt drop any or net_raw
resource "kubernetes_pod" "fail2" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

      security_context {
        capabilities {
          add = ["NET_BIND_SERVICE"]
        }
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
      name  = "example2"

      security_context {
        capabilities {
          drop = ["ALL"]
        }
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

#doesnt drop any or net_raw
resource "kubernetes_pod_v1" "fail2" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

      security_context {
        capabilities {
          add = ["NET_BIND_SERVICE"]
        }
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
      name  = "example2"

      security_context {
        capabilities {
          drop = ["ALL"]
        }
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

#doesnt drop any or net_raw
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
          name  = "example"

          security_context {
            capabilities {
              add = ["NET_BIND_SERVICE"]
            }
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
          name  = "example2"

          security_context {
            capabilities {
              drop = ["ALL"]
            }
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
          name  = "example"

          security_context {
            capabilities {
              add = ["NET_BIND_SERVICE"]
            }
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
          name  = "example2"

          security_context {
            capabilities {
              drop = ["ALL"]
            }
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

#wrong drop
resource "kubernetes_pod" "fail3" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

      security_context {
        capabilities {
          drop = ["NET_BIND_SERVICE"]
        }
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


#wrong drop
resource "kubernetes_pod_v1" "fail3" {
  metadata {
    name = "terraform-example"
  }

  spec {

    container {
      image = "nginx:1.7.9"
      name  = "example"

      security_context {
        capabilities {
          drop = ["NET_BIND_SERVICE"]
        }
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

#wrong drop
resource "kubernetes_deployment" "fail3" {
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
          name  = "example"

          security_context {
            capabilities {
              add = ["NET_BIND_SERVICE"]
            }
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
          name  = "example2"

          security_context {
            capabilities {
              drop = ["ALL"]
            }
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

#wrong drop
resource "kubernetes_deployment_v1" "fail3" {
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
          name  = "example"

          security_context {
            capabilities {
              add = ["NET_BIND_SERVICE"]
            }
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
          name  = "example2"

          security_context {
            capabilities {
              drop = ["ALL"]
            }
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
      name  = "example"

      security_context {
        capabilities {
          drop = ["NET_BIND_SERVICE", "ALL"]
        }
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
      name  = "example2"

      security_context {
        capabilities {
          drop = ["ALL"]
        }
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
      name  = "example"

      security_context {
        capabilities {
          drop = ["NET_BIND_SERVICE", "ALL"]
        }
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
      name  = "example2"

      security_context {
        capabilities {
          drop = ["ALL"]
        }
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
          name  = "example"

          security_context {
            capabilities {
              drop = ["NET_BIND_SERVICE", "ALL"]
            }
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
          name  = "example2"

          security_context {
            capabilities {
              drop = ["ALL"]
            }
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
          name  = "example"

          security_context {
            capabilities {
              drop = ["NET_BIND_SERVICE", "ALL"]
            }
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
          name  = "example2"

          security_context {
            capabilities {
              drop = ["ALL"]
            }
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
