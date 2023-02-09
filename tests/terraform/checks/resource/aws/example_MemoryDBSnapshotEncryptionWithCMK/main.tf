resource "aws_memorydb_snapshot" "fail" {
  name                     = "pike"
  cluster_name = "sato"
}

resource "aws_memorydb_snapshot" "pass" {
  cluster_name = "sato"
  name                     = "pike"
  kms_key_arn              = aws_kms_key.example.arn
}

