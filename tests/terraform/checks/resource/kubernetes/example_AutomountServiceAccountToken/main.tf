# PASS: automount_service_account_token explicitly set to false
resource "kubernetes_pod" "pass" {
  metadata {
    name = "pass"
  }
  spec {
    automount_service_account_token = false
    container {
      name  = "test"
      image = "nginx"
    }
  }
}

# PASS: deployment with automount_service_account_token = false
resource "kubernetes_deployment" "pass" {
  metadata {
    name = "pass"
  }
  spec {
    selector {
      match_labels = {
        app = "test"
      }
    }
    template {
      metadata {
        labels = {
          app = "test"
        }
      }
      spec {
        automount_service_account_token = false
        container {
          name  = "test"
          image = "nginx"
        }
      }
    }
  }
}

# FAIL: automount_service_account_token set to true
resource "kubernetes_pod" "fail" {
  metadata {
    name = "fail"
  }
  spec {
    automount_service_account_token = true
    container {
      name  = "test"
      image = "nginx"
    }
  }
}

# FAIL: automount_service_account_token not set (defaults to true)
resource "kubernetes_pod" "fail2" {
  metadata {
    name = "fail2"
  }
  spec {
    container {
      name  = "test"
      image = "nginx"
    }
  }
}

# FAIL: deployment without automount_service_account_token
resource "kubernetes_deployment" "fail" {
  metadata {
    name = "fail"
  }
  spec {
    selector {
      match_labels = {
        app = "test"
      }
    }
    template {
      metadata {
        labels = {
          app = "test"
        }
      }
      spec {
        container {
          name  = "test"
          image = "nginx"
        }
      }
    }
  }
}
