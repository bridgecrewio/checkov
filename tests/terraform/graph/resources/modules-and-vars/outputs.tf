output "bucket_domain_name" {
  value       = module.this.enabled ? join("", aws_s3_bucket.default.*.bucket_domain_name) : ""
  description = "FQDN of bucket"
}

output "bucket_regional_domain_name" {
  value       = module.this.enabled ? join("", aws_s3_bucket.default.*.bucket_regional_domain_name) : ""
  description = "The bucket region-specific domain name"
}

output "bucket_id" {
  value       = module.this.enabled ? join("", aws_s3_bucket.default.*.id) : ""
  description = "Bucket Name (aka ID)"
}

output "bucket_arn" {
  value       = module.this.enabled ? join("", aws_s3_bucket.default.*.arn) : ""
  description = "Bucket ARN"
}

output "bucket_region" {
  value       = module.this.enabled ? join("", aws_s3_bucket.default.*.region) : ""
  description = "Bucket region"
}

output "enabled" {
  value       = module.this.enabled
  description = "Is module enabled"
}

output "user_enabled" {
  value       = var.user_enabled
  description = "Is user creation enabled"
}

output "user_name" {
  value       = module.s3_user.user_name
  description = "Normalized IAM user name"
}

output "user_arn" {
  value       = module.s3_user.user_arn
  description = "The ARN assigned by AWS for the user"
}

output "user_unique_id" {
  value       = module.s3_user.user_unique_id
  description = "The user unique ID assigned by AWS"
}

output "access_key_id" {
  sensitive   = true
  value       = module.s3_user.access_key_id
  description = "The access key ID"
}

output "secret_access_key" {
  sensitive   = true
  value       = module.s3_user.secret_access_key
  description = "The secret access key. This will be written to the state file in plain-text"
}
