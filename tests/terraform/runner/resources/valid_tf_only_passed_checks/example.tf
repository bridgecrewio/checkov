resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true
  versioning {
    enabled    = true
    mfa_delete = true
  }
  logging {
    target_bucket = "${aws_s3_bucket.log_bucket.id}"
    target_prefix = "log/"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.mykey.arn}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
  acl = "private"
  tags = merge(
      var.common_tags,
  {
    name = "VM Virtual Machine"
    group = "foo"
  }
  )
}

data "aws_caller_identity" "current" {}

provider "kubernetes" {
  version                = "1.10.0"
  host                   = module.aks_cluster.kube_config.0.host
  client_certificate     = base64decode(module.aks_cluster.kube_config.0.client_certificate)
  client_key             = base64decode(module.aks_cluster.kube_config.0.client_key)
  cluster_ca_certificate = base64decode(module.aks_cluster.kube_config.0.cluster_ca_certificate)
}

module "new_relic" {
  source                            = "s3::https://s3.amazonaws.com/my-artifacts/new-relic-k8s-0.2.5.zip"
  kubernetes_host                   = module.aks_cluster.kube_config.0.host
  kubernetes_client_certificate     = base64decode(module.aks_cluster.kube_config.0.client_certificate)
  kubernetes_client_key             = base64decode(module.aks_cluster.kube_config.0.client_key)
  kubernetes_cluster_ca_certificate = base64decode(module.aks_cluster.kube_config.0.cluster_ca_certificate)
  cluster_name                      = module.naming_conventions.aks_name
  new_relic_license                 = data.vault_generic_secret.new_relic_license.data["license"]
  cluster_ca_bundle_b64             = module.aks_cluster.kube_config.0.cluster_ca_certificate
  module_depends_on                 = [null_resource.delay_aks_deployments]
}