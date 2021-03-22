locals {
  name      = "test_local_name"
  namespace = "test_namespace"

  labels = {
    "app.kubernetes.io/name"       = local.name
    "app.kubernetes.io/instance"   = "hpa"
    "app.kubernetes.io/version"    = "1.0.0"
    "app.kubernetes.io/managed-by" = "terraform"
  }
}