# fails no spec
resource "kubernetes_pod" "fail2" {
  metadata {
    name = "terraform-example"
  }
}

# fails no spec
resource "kubernetes_pod_v1" "fail2" {
  metadata {
    name = "terraform-example"
  }
}

# fails no resource
resource "kubernetes_pod" "fail3" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

# fails no resource
resource "kubernetes_pod_v1" "fail3" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

# fails no requests
resource "kubernetes_pod" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

      resources {

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

# fails no requests
resource "kubernetes_pod_v1" "fail" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

      resources {

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

# fails no memory requests
resource "kubernetes_pod" "fail4" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

      resources {
        requests = "x"
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

# fails no memory requests
resource "kubernetes_pod_v1" "fail4" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

      resources {
        requests = "x"
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

resource "kubernetes_pod" "pass" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

      resources {
        requests = {
          memory = "1Gi"
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

resource "kubernetes_pod_v1" "pass" {
  metadata {
    name = "terraform-example"
  }

  spec {
    host_ipc = true
    host_pid = true

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

      resources {
        requests = {
          memory = "1Gi"
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
