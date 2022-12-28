variable "bucket"{
  default = aws_s3_bucket.example.id
}

variable "block_public_acls" {
  type = bool
}