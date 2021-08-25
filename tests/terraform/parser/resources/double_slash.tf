resource "helm_release" "test" {
  name       = "influxdb"
  repository = "https://helm.influxdata.com"
  chart      = "influxdb"
  namespace  = "influxdb"
  set {
    name  = "ingress.annotations.kubernetes\\.io/ingress\\.class"
    value = var.influxdb_ingress_annotations_kubernetes_ingress_class
  }
}