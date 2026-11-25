locals {
  a = aws_elasticache_replication_group.widget[0].primary_endpoint_address
  b = var.enable_other && (var.other_mode == "required" || var.other_secret_ref != null)
}
