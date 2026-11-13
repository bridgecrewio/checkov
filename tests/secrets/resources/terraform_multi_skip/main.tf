resource "aws_instance" "test" {
  # checkov:skip=CKV_SECRET_6,CKV_SECRET_2:known test values
  secret_key = "kX9vQm2nR8pLw4tY7uI1oP5aS3dF6gH0jK9lM2nB4vC8"
}
