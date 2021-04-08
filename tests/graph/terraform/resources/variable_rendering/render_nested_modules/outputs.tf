output "bucket_acl" {
  value = aws_s3_bucket.template_bucket.acl

  depends_on = [
      aws_eip.ip
  ]
}
