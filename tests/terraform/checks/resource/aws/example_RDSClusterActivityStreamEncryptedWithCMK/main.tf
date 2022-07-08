resource "aws_rds_cluster_activity_stream" "pass" {
  resource_arn = aws_rds_cluster.default.arn
  mode         = "async"
  kms_key_id   = aws_kms_key.default.key_id

  depends_on = [aws_rds_cluster_instance.default]
}


resource "aws_rds_cluster_activity_stream" "fail" {
  resource_arn = aws_rds_cluster.default.arn
  mode         = "async"

  depends_on = [aws_rds_cluster_instance.default]
}