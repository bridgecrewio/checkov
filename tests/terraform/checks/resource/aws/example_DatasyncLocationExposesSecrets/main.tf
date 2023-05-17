resource "aws_datasync_location_object_storage" "pass" {
  agent_arns      = [aws_datasync_agent.example.arn]
  server_hostname = "example"
  bucket_name     = "example"
}

resource "aws_datasync_location_object_storage" "fail" {
  agent_arns      = [aws_datasync_agent.example.arn]
  server_hostname = "example"
  bucket_name     = "example"
  secret_key="OWTHATSBLOWNIT"  # checkov:skip=CKV_SECRET_6 test secret
}