locals {
  # This is intentionally missing the closing quote
  s3_access_logs_prefix = "${replace(var.cdn_logging_prefix, "cdn", "s3")/${var.bucket_name}}
}
