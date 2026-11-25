resource "aws_elasticache_replication_group" "widget" {
  count = 1
  # checkov:skip=CKV_AWS_31: test
  # checkov:skip=CKV_AWS_30: test
  # checkov:skip=CKV_AWS_191: test
  # checkov:skip=CKV_AWS_29: test
  # checkov:skip=CKV2_AWS_50: test
  replication_group_id       = "widget"
  description                = "widget"
  auth_token_update_strategy = local.b ? "ROTATE" : null
}
