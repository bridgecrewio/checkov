
#image is tiller
resource "kubernetes_pod" "fail" {
  metadata {
    name = "tiller-deploy"
  }

  spec {
    container {
      image = "tiller-image"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

#image is tiller
resource "kubernetes_pod_v1" "fail" {
  metadata {
    name = "tiller-deploy"
  }

  spec {
    container {
      image = "tiller-image"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

#image is tiller
resource "kubernetes_deployment" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "app"
      }
    }

    template {
      metadata {
        labels = {
          app = "app"
        }
      }

      spec {
        container {
          image = "tiller-image"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#image is tiller
resource "kubernetes_deployment_v1" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "app"
      }
    }

    template {
      metadata {
        labels = {
          app = "app"
        }
      }

      spec {
        container {
          image = "tiller-image"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#label is tiller
resource "kubernetes_pod" "fail2" {
  metadata {
    labels = {
      name = "tiller"
    }
  }

  spec {
    container {
      image = "nuthin-dodgy"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

#label is tiller
resource "kubernetes_pod_v1" "fail2" {
  metadata {
    labels = {
      name = "tiller"
    }
  }

  spec {
    container {
      image = "nuthin-dodgy"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

    #app is helm
    resource "kubernetes_deployment" "fail3" {
      metadata {
        name = "terraform-example"
        labels = {
          app = "helm"
        }
      }

      spec {
        replicas = 3

        selector {
          match_labels = {
            app = "nginx"
          }
        }

        template {
          metadata {
            labels = {
              app = "nginx"
            }
          }

          spec {
            container {
              image = "nuthin-dodgy"
              name  = "example22"

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

              resources {
                requests = {
                  cpu    = "250m"
                  memory = "50Mi"
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

    #app is helm
    resource "kubernetes_deployment_v1" "fail3" {
      metadata {
        name = "terraform-example"
        labels = {
          app = "helm"
        }
      }

      spec {
        replicas = 3

        selector {
          match_labels = {
            app = "nginx"
          }
        }

        template {
          metadata {
            labels = {
              app = "nginx"
            }
          }

          spec {
            container {
              image = "nuthin-dodgy"
              name  = "example22"

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

              resources {
                requests = {
                  cpu    = "250m"
                  memory = "50Mi"
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

    #app is helm
    resource "kubernetes_deployment" "fail5" {
      metadata {
        name = "terraform-example"
        labels = {
          app = "nginx"
        }
      }

      spec {
        replicas = 3

        selector {
          match_labels = {
            app = "helm"
          }
        }

        template {
          metadata {
            labels = {
              app = "helm"
            }
          }

          spec {
            container {
              image = "nuthin-dodgy"
              name  = "example22"

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

              resources {
                requests = {
                  cpu    = "250m"
                  memory = "50Mi"
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

    resource "kubernetes_deployment_v1" "fail5" {
      metadata {
        name = "terraform-example"
        labels = {
          app = "nginx"
        }
      }

      spec {
        replicas = 3

        selector {
          match_labels = {
            app = "helm"
          }
        }

        template {
          metadata {
            labels = {
              app = "helm"
            }
          }

          spec {
            container {
              image = "nuthin-dodgy"
              name  = "example22"

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

              resources {
                requests = {
                  cpu    = "250m"
                  memory = "50Mi"
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

#label is tiller
resource "kubernetes_deployment" "fail2" {
  metadata {
    name = "terraform-example"
    labels = {
      name = "tiller"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        name = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          name = "nginx"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#label is tiller
resource "kubernetes_deployment_v1" "fail2" {
  metadata {
    name = "terraform-example"
    labels = {
      name = "tiller"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        name = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          name = "nginx"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#label is tiller
resource "kubernetes_deployment" "fail4" {
  metadata {
    name = "terraform-example"
    labels = {
      name = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        name = "tiller"
      }
    }

    template {
      metadata {
        labels = {
          name = "tiller"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#label is tiller
resource "kubernetes_deployment_v1" "fail4" {
  metadata {
    name = "terraform-example"
    labels = {
      name = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        name = "tiller"
      }
    }

    template {
      metadata {
        labels = {
          name = "tiller"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#app is helm
resource "kubernetes_pod" "fail3" {
  metadata {
    labels = {
       app = "helm"
    }
  }

  spec {
    container {
      image = "nuthin-dodgy"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

#app is helm
resource "kubernetes_pod_v1" "fail3" {
  metadata {
    labels = {
      app = "helm"
    }
  }

  spec {
    container {
      image = "nuthin-dodgy"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

#app is helm
resource "kubernetes_deployment" "fail3" {
  metadata {
    name = "terraform-example"
    labels = {
      app = "helm"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        name = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          name = "nginx"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#app is helm
resource "kubernetes_deployment_v1" "fail3" {
  metadata {
    name = "terraform-example"
    labels = {
      app = "helm"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        name = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          name = "nginx"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#app is helm
resource "kubernetes_deployment" "fail5" {
  metadata {
    name = "terraform-example"
    labels = {
      app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "helm"
      }
    }

    template {
      metadata {
        labels = {
          app = "helm"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#app is helm
resource "kubernetes_deployment_v1" "fail5" {
  metadata {
    name = "terraform-example"
    labels = {
      app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "helm"
      }
    }

    template {
      metadata {
        labels = {
          app = "helm"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#app is helm
resource "kubernetes_pod" "pass" {
  metadata {
   name="terraform-example"
  }

  spec {
    container {
      image = "nuthin-dodgy"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

#app is helm
resource "kubernetes_pod_v1" "pass" {
  metadata {
    name="terraform-example"
  }

  spec {
    container {
      image = "nuthin-dodgy"
      name  = "example22"

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

      resources {
        requests = {
          cpu    = "250m"
          memory = "50Mi"
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

#app is helm
resource "kubernetes_deployment" "pass" {
  metadata {
    name = "terraform-example"
    labels = {
      app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          app = "nginx"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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

#app is helm
resource "kubernetes_deployment_v1" "pass" {
  metadata {
    name = "terraform-example"
    labels = {
      app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          app = "nginx"
        }
      }

      spec {
        container {
          image = "nuthin-dodgy"
          name  = "example22"

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

          resources {
            requests = {
              cpu    = "250m"
              memory = "50Mi"
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