resource "aws_eks_cluster" "example_direct" {
  name     = "example"
  enabled_cluster_log_types =  ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}

resource "aws_eks_cluster" "example_var" {
  name     = "example"
  enabled_cluster_log_types = var.log_types_enabled
}

variable "log_types_enabled" {
 type = list(string)
 default = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}