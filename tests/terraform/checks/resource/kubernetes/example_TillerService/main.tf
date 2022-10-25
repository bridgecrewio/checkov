resource "kubernetes_service" "fail2" {
  metadata {
    name = "terraform-example"
    labels = {
      app="helm"
      name="tiller"
    }
  }
  spec {
    selector = {
      app = kubernetes_pod.example.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_service_v1" "fail2" {
  metadata {
    name = "terraform-example"
    labels = {
      app="helm"
      name="tiller"
    }
  }
  spec {
    selector = {
      app = kubernetes_pod_v1.example.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_service" "fail" {
  metadata {
    name = "terraform-example"
  }
  spec {
    selector = {
      app = "helm"
      name= "tiller"
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_service_v1" "fail" {
  metadata {
    name = "terraform-example"
  }
  spec {
    selector = {
      app = "helm"
      name= "tiller"
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_service" "pass" {
  metadata {
    name = "terraform-example"
  }
  spec {
    selector = {
      app = kubernetes_pod.example.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_service_v1" "pass" {
  metadata {
    name = "terraform-example"
  }
  spec {
    selector = {
      app = kubernetes_pod_v1.example.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_service" "fail3" {
  metadata {

    labels = var.isNull == "not_null" ? {
      app="helm"
      name="tiller"
    } : null

  }
  spec {}
}

resource "kubernetes_service_v1" "fail3" {
  metadata {

    labels = var.isNull == "not_null" ? {
      app="helm"
      name="tiller"
    } : null

  }
  spec {}
}
