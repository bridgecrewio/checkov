resource "aws_db_instance" "enabled" {
  allocated_storage                     = var.instance["allocated_storage"]
  auto_minor_version_upgrade            = var.instance["auto_minor_version_upgrade"]
  availability_zone                     = var.instance["availability_zone"]
  backup_retention_period               = var.instance["backup_retention_period"]
  backup_window                         = var.instance["backup_window"]
  copy_tags_to_snapshot                 = var.instance["copy_tags_to_snapshot"]
  db_subnet_group_name                  = aws_db_subnet_group.access[0].name
  deletion_protection                   = true
  enabled_cloudwatch_logs_exports       = []
  engine                                = var.instance["engine"]
  engine_version                        = var.instance["engine_version"]
  iam_database_authentication_enabled   = var.instance["iam_database_authentication_enabled"]
  instance_class                        = var.instance["instance_class"]
  iops                                  = var.instance["iops"]
  kms_key_id                            = var.storage_encrypted ? data.aws_kms_key.rds.arn : null
  license_model                         = var.instance["license_model"]
  maintenance_window                    = var.instance["maintenance_window"]
  max_allocated_storage                 = var.instance["max_allocated_storage"]
  monitoring_interval                   = var.instance["monitoring_interval"]
  monitoring_role_arn                   = var.monitoring_role_arn
  multi_az                              = var.instance["multi_az"]
  name                                  = var.instance["name"]
  option_group_name                     = var.instance["option_group_name"]
  parameter_group_name                  = var.custom_db_group_name
  password                              = var.instance_password
  performance_insights_enabled          = var.instance["performance_insights_enabled"]
  performance_insights_kms_key_id       = data.aws_kms_key.rds.arn
  performance_insights_retention_period = var.instance["performance_insights_retention_period"]
  port                                  = var.instance["port"]
  publicly_accessible                   = false
  security_group_names                  = var.instance["security_group_names"]
  skip_final_snapshot                   = var.instance["skip_final_snapshot"]
  snapshot_identifier                   = var.instance["snapshot_identifier"]
  storage_encrypted                     = var.storage_encrypted
  storage_type                          = var.instance["storage_type"]
  tags                                  = var.common_tags
  username                              = var.instance["username"]
}

resource "aws_db_instance" "disabled" {
  allocated_storage                     = var.instance["allocated_storage"]
  auto_minor_version_upgrade            = var.instance["auto_minor_version_upgrade"]
  availability_zone                     = var.instance["availability_zone"]
  backup_retention_period               = var.instance["backup_retention_period"]
  backup_window                         = var.instance["backup_window"]
  copy_tags_to_snapshot                 = var.instance["copy_tags_to_snapshot"]
  db_subnet_group_name                  = aws_db_subnet_group.access[0].name
  deletion_protection                   = false
  enabled_cloudwatch_logs_exports       = []
  engine                                = var.instance["engine"]
  engine_version                        = var.instance["engine_version"]
  iam_database_authentication_enabled   = var.instance["iam_database_authentication_enabled"]
  instance_class                        = var.instance["instance_class"]
  iops                                  = var.instance["iops"]
  kms_key_id                            = var.storage_encrypted ? data.aws_kms_key.rds.arn : null
  license_model                         = var.instance["license_model"]
  maintenance_window                    = var.instance["maintenance_window"]
  max_allocated_storage                 = var.instance["max_allocated_storage"]
  monitoring_interval                   = var.instance["monitoring_interval"]
  monitoring_role_arn                   = var.monitoring_role_arn
  multi_az                              = var.instance["multi_az"]
  name                                  = var.instance["name"]
  option_group_name                     = var.instance["option_group_name"]
  parameter_group_name                  = var.custom_db_group_name
  password                              = var.instance_password
  performance_insights_enabled          = var.instance["performance_insights_enabled"]
  performance_insights_kms_key_id       = data.aws_kms_key.rds.arn
  performance_insights_retention_period = var.instance["performance_insights_retention_period"]
  port                                  = var.instance["port"]
  publicly_accessible                   = false
  security_group_names                  = var.instance["security_group_names"]
  skip_final_snapshot                   = var.instance["skip_final_snapshot"]
  snapshot_identifier                   = var.instance["snapshot_identifier"]
  storage_encrypted                     = var.storage_encrypted
  storage_type                          = var.instance["storage_type"]
  tags                                  = var.common_tags
  username                              = var.instance["username"]
}

resource "aws_db_instance" "missing" {
  allocated_storage                     = var.instance["allocated_storage"]
  auto_minor_version_upgrade            = var.instance["auto_minor_version_upgrade"]
  availability_zone                     = var.instance["availability_zone"]
  backup_retention_period               = var.instance["backup_retention_period"]
  backup_window                         = var.instance["backup_window"]
  copy_tags_to_snapshot                 = var.instance["copy_tags_to_snapshot"]
  db_subnet_group_name                  = aws_db_subnet_group.access[0].name
  enabled_cloudwatch_logs_exports       = []
  engine                                = var.instance["engine"]
  engine_version                        = var.instance["engine_version"]
  iam_database_authentication_enabled   = var.instance["iam_database_authentication_enabled"]
  instance_class                        = var.instance["instance_class"]
  iops                                  = var.instance["iops"]
  kms_key_id                            = var.storage_encrypted ? data.aws_kms_key.rds.arn : null
  license_model                         = var.instance["license_model"]
  maintenance_window                    = var.instance["maintenance_window"]
  max_allocated_storage                 = var.instance["max_allocated_storage"]
  monitoring_interval                   = var.instance["monitoring_interval"]
  monitoring_role_arn                   = var.monitoring_role_arn
  multi_az                              = var.instance["multi_az"]
  name                                  = var.instance["name"]
  option_group_name                     = var.instance["option_group_name"]
  parameter_group_name                  = var.custom_db_group_name
  password                              = var.instance_password
  performance_insights_enabled          = var.instance["performance_insights_enabled"]
  performance_insights_kms_key_id       = data.aws_kms_key.rds.arn
  performance_insights_retention_period = var.instance["performance_insights_retention_period"]
  port                                  = var.instance["port"]
  publicly_accessible                   = false
  security_group_names                  = var.instance["security_group_names"]
  skip_final_snapshot                   = var.instance["skip_final_snapshot"]
  snapshot_identifier                   = var.instance["snapshot_identifier"]
  storage_encrypted                     = var.storage_encrypted
  storage_type                          = var.instance["storage_type"]
  tags                                  = var.common_tags
  username                              = var.instance["username"]
}


resource "aws_rds_cluster" "missing" {
  cluster_identifier   = "example"
  db_subnet_group_name = aws_db_subnet_group.example.name
  engine_mode          = "multimaster"
  master_password      = "barbarbarbar"
  master_username      = "foo"
  skip_final_snapshot  = true
}

resource "aws_rds_cluster" "false" {
  cluster_identifier   = "example"
  db_subnet_group_name = aws_db_subnet_group.example.name
  engine_mode          = "multimaster"
  deletion_protection  = false
  master_password      = "barbarbarbar"
  master_username      = "foo"
  skip_final_snapshot  = true
}

resource "aws_rds_cluster" "true" {
  cluster_identifier   = "example"
  db_subnet_group_name = aws_db_subnet_group.example.name
  deletion_protection  = true
  engine_mode          = "multimaster"
  master_password      = "barbarbarbar"
  master_username      = "foo"
  skip_final_snapshot  = true
}