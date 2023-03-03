output "user_name" {
  value       = join("", aws_iam_user.default.*.name)
  description = "Normalized IAM user name"
}

output "user_arn" {
  value       = join("", aws_iam_user.default.*.arn)
  description = "The ARN assigned by AWS for this user"
}

output "user_unique_id" {
  value       = join("", aws_iam_user.default.*.unique_id)
  description = "The unique ID assigned by AWS"
}

output "access_key_id" {
  value       = join("", aws_iam_access_key.default.*.id)
  description = "The access key ID"
}

output "secret_access_key" {
  sensitive   = true
  value       = join("", aws_iam_access_key.default.*.secret)
  description = "The secret access key. This will be written to the state file in plain-text"
}

output "ses_smtp_password" {
  sensitive   = true
  value       = join("", aws_iam_access_key.default.*.ses_smtp_password)
  description = "The secret access key converted into an SES SMTP password by applying AWS's documented conversion algorithm."
}
