output "cloudwatch_log_group_name" {
  description = "Name of Cloudwatch log group"
  value       = try(aws_cloudwatch_log_group.this[0].name, "")
}

output "cloudwatch_log_group_arn" {
  description = "ARN of Cloudwatch log group"
  value       = try(aws_cloudwatch_log_group.this[0].arn, "")
}
