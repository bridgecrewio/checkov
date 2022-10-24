resource "aws_fsx_lustre_file_system" "pass" {
  storage_capacity            = 1200
  subnet_ids                  = [aws_subnet.test1.id]
  deployment_type             = "PERSISTENT_1"
  per_unit_storage_throughput = 50
  kms_key_id                  = aws_kms_key.test1.arn
}

resource "aws_fsx_lustre_file_system" "fail" {
  storage_capacity            = 1200
  subnet_ids                  = [aws_subnet.test1.id]
  deployment_type             = "PERSISTENT_1"
  per_unit_storage_throughput = 50
}