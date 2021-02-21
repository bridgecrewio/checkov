## Outputs

output "cluster_name" {
  value = "${aws_eks_cluster.eks.name}"
}

output "kubeconfig" {
  value = "${local.kubeconfig}"
}

output "aws-auth-cm.yaml" {
  value = "${local.aws-auth-cm}"
}

//output "config_map_aws_auth" {
//  value = "${local.config_map_aws_auth}"
//}