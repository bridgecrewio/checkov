# pass

# App Runner

resource "aws_security_group" "pass_app_runner" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_apprunner_vpc_connector" "pass_app_runner" {
  vpc_connector_name = "name"
  subnets            = ["subnet1", "subnet2"]
  security_groups    = [aws_security_group.pass_app_runner.id]
}

# App Stream Fleet

resource "aws_security_group" "pass_appstream_fleet" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_appstream_fleet" "pass_appstream_fleet" {
  name          = "name"
  instance_type = "stream.standard.large"
  compute_capacity {
    desired_instances = 1
  }
  vpc_config {
    security_groups_ids = [aws_security_group.pass_appstream_fleet.id]
  }
}

# Batch

resource "aws_security_group" "pass_batch" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_batch_compute_environment" "pass_batch" {
  service_role = "aws_iam_role.batch.arn"
  type         = "MANAGED"

  compute_resources {
    max_vcpus          = 16
    security_group_ids = [aws_security_group.pass_batch.id]
    subnets            = ["aws_subnet.this.id"]
    type               = "FARGATE"
  }
}

# CodeBuild

resource "aws_security_group" "pass_codebuild" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_codebuild_project" "pass_codebuild" {
  name         = "build"
  service_role = "aws_iam_role.codebuild.arn"

  artifacts {
    type = "NO_ARTIFACTS"
  }
  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:5.0"
    type         = "LINUX_CONTAINER"
  }
  source {
    type = "S3"
  }
  vpc_config {
    security_group_ids = [aws_security_group.pass_codebuild.id]
    subnets            = ["aws_subnet.public_a.id"]
    vpc_id             = "aws_vpc.vpc.id"
  }
}

# Codestar

resource "aws_security_group" "pass_codestar" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_codestarconnections_host" "pass_codestar" {
  name              = "star"
  provider_endpoint = "https://github.com/bridgecrewio/checkov"
  provider_type     = "GitHubEnterpriseServer"
  vpc_configuration {
    vpc_id             = "aws_vpc.vpc.id"
    security_group_ids = [aws_security_group.pass_codestar.id]
    subnet_ids         = ["aws_subnet.public_a.id"]
  }
  provider = aws.primary
}

# DMS

resource "aws_security_group" "pass_dms" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_dms_replication_instance" "pass_dms" {
  replication_instance_class = "dms.t3.micro"
  replication_instance_id    = "dms"
  vpc_security_group_ids     = [aws_security_group.pass_dms.id]
}

#DMS Serverless

resource "aws_security_group" "pass_dms_serverless" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_dms_replication_config" "pass_dms_serverless" {
  replication_config_identifier = "dms"
  resource_identifier           = "dms"
  replication_type              = "cdc"
  source_endpoint_arn           = "aws_dms_endpoint.source.endpoint_arn"
  target_endpoint_arn           = "aws_dms_endpoint.target.endpoint_arn"
  table_mappings                = <<EOF
  {
    "rules":[{"rule-type":"selection","rule-id":"1","rule-name":"1","rule-action":"include","object-locator":{"schema-name":"%%","table-name":"%%"}}]
  }
EOF

  compute_config {
    max_capacity_units           = "1"
    vpc_security_group_ids       = [aws_security_group.pass_dms_serverless.id]
  }
}

# DocDB

resource "aws_security_group" "pass_docdb" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_docdb_cluster" "pass_docdb" {
  vpc_security_group_ids = [aws_security_group.pass_docdb.id]
}

# EC2

resource "aws_security_group" "pass_ec2" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "pass_ec2" {
  ami             = "data.aws_ami.ubuntu.id"
  instance_type   = "t3.micro"
  security_groups = [aws_security_group.pass_ec2.id]
}

resource "aws_security_group" "pass_ec2_client_vpn_endpoint" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ec2_client_vpn_endpoint" "pass_ec2_client_vpn_endpoint" {
  server_certificate_arn = "aws_acm_certificate.cert.arn"
  client_cidr_block      = "10.0.0.0/16"

  vpc_id             = "vpc_id"
  security_group_ids = [aws_security_group.pass_ec2_client_vpn_endpoint.id]
}

resource "aws_security_group" "pass_ec2_client_vpn" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ec2_client_vpn_network_association" "pass_ec2_client_vpn" {
  client_vpn_endpoint_id = "aws_ec2_client_vpn_endpoint.this.id"
  subnet_id              = "aws_subnet.this.id"
  security_groups        = [aws_security_group.pass_ec2_client_vpn.id]
}

resource "aws_security_group" "pass_ec2_launch_config" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_launch_configuration" "pass_ec2_launch_config" {
  image_id        = "data.aws_ami.ubuntu.id"
  instance_type   = "t3.micro"
  security_groups = [aws_security_group.pass_ec2_launch_config.id]
}

resource "aws_security_group" "pass_ec2_launch_template" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_launch_template" "pass_ec2_launch_template" {
  image_id               = "data.aws_ami.ubuntu.id"
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.pass_ec2_launch_template.id]
}

resource "aws_security_group" "pass_ec2_spot_fleet_request" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ec2_spot_fleet_request" "pass_ec2_spot_fleet_request" {
  ami             = "aws_ec2_spot_fleet_request.this.id"
  instance_type   = "t3.micro"
  security_groups = [aws_security_group.pass_ec2_spot_fleet_request.id]
}

# ECS

resource "aws_security_group" "pass_ecs" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_service" "pass_ecs" {
  name = "service"

  network_configuration {
    subnets         = ["aws_subnet.public_a.id"]
    security_groups = [aws_security_group.pass_ecs.id]
  }
}

# EFS

resource "aws_security_group" "pass_efs" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_efs_mount_target" "pass_efs" {
  file_system_id  = "aws_efs_file_system.efs.id"
  subnet_id       = "aws_subnet.public_a.id"
  security_groups = [aws_security_group.pass_efs.id]
}

# EKS

resource "aws_security_group" "pass_eks" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_eks_cluster" "pass_eks" {
  name     = "eks"
  role_arn = "aws_iam_role.eks.arn"
  vpc_config {
    security_group_ids = [aws_security_group.pass_eks.id]
    subnet_ids         = ["aws_subnet.public_a.id"]
  }
}

resource "aws_security_group" "pass_eks_node" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_eks_node_group" "pass_eks_node" {
  cluster_name    = "eks"
  node_group_name = "eks"
  node_role_arn   = "aws_iam_role.eks.arn"
  subnet_ids      = ["aws_subnet.public_a.id"]

  remote_access {
    ec2_ssh_key               = "ec2_ssh_key"
    source_security_group_ids = [aws_security_group.pass_eks_node.id]
  }
  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }
}

# Elasticache

resource "aws_security_group" "pass_elasticache" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_cluster" "pass_elasticache" {
  cluster_id         = "cache"
  security_group_ids = [aws_security_group.pass_elasticache.id]
}

resource "aws_security_group" "pass_elasticache_replication_group" {
  description = "elasticache redis security group"
  name        = "test_elasticache_replication_group"
  vpc_id      = var.vpc_id

}

resource "aws_security_group_rule" "elasticache_ingress" {
  description       = "elasticache ingress rule"
  type              = "ingress"
  from_port         = 1234
  to_port           = 1234
  protocol          = "TCP"
  security_group_id = aws_security_group.pass_elasticache_replication_group.id
}

resource "aws_security_group_rule" "elasticache_egress" {
  description       = "elasticache egress rule"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.pass_elasticache_replication_group.id
}

resource "aws_elasticache_replication_group" "pass_elasticache_replication_group" {
  replication_group_id          = "repl"
  replication_group_description = "Replication group for Elasticache"
  node_type                     = "cache.m3.large"
  number_cache_clusters         = 5
  engine                        = "redis"
  port                          = 1234
  subnet_group_name             = "subnet_group_name"
  security_group_ids            = [aws_security_group.pass_elasticache_replication_group.id]
}

# ELB

resource "aws_security_group" "pass_alb" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "pass_alb" {
  load_balancer_type = "application"
  security_groups    = [aws_security_group.pass_alb.id]
}

resource "aws_security_group" "pass_elb" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elb" "pass_elb" {
  security_groups = [aws_security_group.pass_elb.id]

  listener {
    instance_port     = 80
    instance_protocol = "HTTP"
    lb_port           = 443
    lb_protocol       = "HTTPS"
  }
}

resource "aws_security_group" "pass_lb" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "pass_lb" {
  load_balancer_type = "application"
  security_groups    = [aws_security_group.pass_lb.id]
}

# EMR

resource "aws_security_group" "pass_emr" {
  name        = "block_access"
  description = "Block all traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }
}

resource "aws_emr_cluster" "pass_emr" {
  name                   = "var.cluster_name"
  release_label          = "var.release_label"
  security_configuration = "aws_emr_security_configuration.examplea.name"

  ec2_attributes {
    subnet_id                         = "var.subnet_id"
    emr_managed_master_security_group = aws_security_group.pass_emr.id
    emr_managed_slave_security_group  = aws_security_group.pass_emr.id
    instance_profile                  = "aws_iam_instance_profile.examplea.arn"
  }

  service_role = "aws_iam_role.emr_service.arn"
}

resource "aws_security_group" "pass_emr_studio" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_emr_studio" "pass_emr_studio" {
  auth_mode                   = "SSO"
  default_s3_location         = "s3://example/test"
  engine_security_group_id    = aws_security_group.pass_emr_studio.id
  name                        = "example"
  service_role                = "aws_iam_role.test.arn"
  subnet_ids                  = ["aws_subnet.test.id"]
  user_role                   = "aws_iam_role.test.arn"
  vpc_id                      = "aws_vpc.test.id"
  workspace_security_group_id = aws_security_group.pass_emr_studio.id
}

# ENI

resource "aws_security_group" "pass_eni" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_network_interface" "pass_eni" {
  subnet_id       = "aws_subnet.public_a.id"
  security_groups = [aws_security_group.pass_eni.id]
}

# ES

resource "aws_security_group" "pass_es" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticsearch_domain" "pass_es" {
  domain_name = "es"

  vpc_options {
    security_group_ids = [aws_security_group.pass_es.id]
  }
}

# Glue

resource "aws_security_group" "pass_glue" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_glue_dev_endpoint" "pass_glue" {
  name     = "example"
  role_arn = "aws_iam_role.example.arn"

  security_group_ids = [aws_security_group.pass_glue.id]
}

# Lambda

resource "aws_security_group" "pass_lambda" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lambda_function" "pass_lambda" {
  function_name = "lambda"
  handler       = "lambda.handler"
  role          = "aws_iam_role.lambda.arn"
  runtime       = "python3.8"

  vpc_config {
    security_group_ids = [aws_security_group.pass_lambda.id]
    subnet_ids         = ["aws_subnet.public_a.id"]
  }
}

# MQ

resource "aws_security_group" "pass_mq" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_mq_broker" "pass_mq" {
  broker_name        = "mq"
  engine_type        = "ActiveMQ"
  engine_version     = "5.15.15"
  host_instance_type = "mq.t3.micro"
  security_groups    = [aws_security_group.pass_mq.id]

  user {
    password = "pass"
    username = "user"
  }
}

# MSK

resource "aws_security_group" "pass_msk" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_msk_cluster" "pass_msk" {
  cluster_name           = "msk"
  kafka_version          = "2.8.0"
  number_of_broker_nodes = 1

  broker_node_group_info {
    client_subnets  = ["aws_subnet.public_a.id"]
    ebs_volume_size = 50
    instance_type   = "kafka.m5.large"
    security_groups = [aws_security_group.pass_msk.id]
  }
}

# MWAA

resource "aws_security_group" "pass_mwaa" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_mwaa_environment" "pass_mwaa" {
  dag_s3_path        = "dags/"
  execution_role_arn = "aws_iam_role.mwaa.arn"
  name               = "mwaa"
  source_bucket_arn  = "aws_s3_bucket.mwaa.arn"

  network_configuration {
    security_group_ids = [aws_security_group.pass_mwaa.id]
    subnet_ids         = ["aws_subnet.public_a.id"]
  }

}

# Neptune

resource "aws_security_group" "pass_neptune" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_neptune_cluster" "pass_neptune" {
  vpc_security_group_ids = [aws_security_group.pass_neptune.id]
}

# Quicksight

resource "aws_security_group" "pass_quicksight" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_quicksight_vpc_connection" "pass_quicksight" {
  vpc_connection_id  = "example-connection-id"
  name               = "Example Connection"
  role_arn           = "aws_iam_role.vpc_connection_role.arn"
  security_group_ids = [aws_security_group.pass_quicksight.id]
  subnet_ids         = ["subnet-00000000000000000"]
}

# RDS

resource "aws_security_group" "pass_rds" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "pass_rds" {
  instance_class         = "db.t3.micro"
  vpc_security_group_ids = [aws_security_group.pass_rds.id]
}

resource "aws_security_group" "pass_rds_cluster" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_rds_cluster" "pass_rds_cluster" {
  vpc_security_group_ids = [aws_security_group.pass_rds_cluster.id]
}

# Redshift

resource "aws_security_group" "pass_redshift" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_redshift_cluster" "pass_redshift" {
  cluster_identifier     = "redshift"
  node_type              = "dc2.large"
  vpc_security_group_ids = [aws_security_group.pass_redshift.id]
}

# Sagemaker

resource "aws_security_group" "pass_sagemaker" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_sagemaker_notebook_instance" "pass_sagemaker" {
  instance_type   = "ml.t3.medium"
  name            = "sagemaker"
  role_arn        = "aws_iam_role.sagemaker.arn"
  security_groups = [aws_security_group.pass_sagemaker.id]
}

# VPC

resource "aws_security_group" "pass_vpc_endpoint" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc_endpoint" "pass_vpc_endpoint" {
  vpc_id             = "aws_vpc.this.id"
  service_name       = "com.amazonaws.us-west-2.s3"
  vpc_endpoint_type  = "Interface"
  security_group_ids = [aws_security_group.pass_vpc_endpoint.id]
}

resource "aws_security_group" "pass_vpclattice" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpclattice_service_network_vpc_association" "pass_vpclattice" {
  vpc_identifier             = "aws_vpc.example.id"
  service_network_identifier = "aws_vpclattice_service_network.example.id"
  security_group_ids         = [aws_security_group.pass_vpclattice.id]
}

# fail

resource "aws_security_group" "fail" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_cloudwatch_event_target" "pass_cloudwatch_event" {
  target_id = var.target_id
  arn       = var.arn
  rule      = var.rule
  role_arn  = var.role_arn

  ecs_target {
    launch_type         = var.launch_type
    task_count          = var.task_count
    task_definition_arn = var.task_definition_arn

    network_configuration {
      subnets          = [var.subnet_id]
      security_groups  = [aws_security_group.pass_cloudwatch_event.id]
      assign_public_ip = false
    }
  }

  input = <<EOF
{
  "containerOverrides": [ ]
}
EOF
}

resource "aws_security_group" "pass_cloudwatch_event" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "pass_mq_broker" {
  description = "Managed by Terraform"
  egress {
    #tfsec:ignore:AWS009
    cidr_blocks = ["0.0.0.0/0"]
    description = "Outbound"
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
  }

  ingress {
    cidr_blocks = var.ingress
    description = "MQ port"
    from_port   = 61616
    protocol    = "tcp"
    self        = false
    to_port     = 61616
  }


  name   = var.security_group_name
  vpc_id = var.vpc_id
  tags   = var.common_tags
}

resource "aws_mq_broker" "broker" {
  broker_name = var.mq_broker["name"]

  configuration {
    id       = aws_mq_configuration.broker.id
    revision = aws_mq_configuration.broker.latest_revision
  }

  engine_type         = var.mq_broker["engine_type"]
  engine_version      = var.mq_broker["engine_version"]
  host_instance_type  = var.mq_broker["host_instance_type"]
  deployment_mode     = var.mq_broker["deployment_mode"]
  publicly_accessible = var.mq_broker["publicly_accessible"]
  security_groups     = [aws_security_group.pass_mq_broker.id]

  user {
    username = var.username
    password = var.password
  }

  maintenance_window_start_time {
    day_of_week = var.maintenance_window_start_time["day_of_week"]
    time_of_day = var.maintenance_window_start_time["time_of_day"]
    time_zone   = var.maintenance_window_start_time["time_zone"]
  }

  encryption_options {
    kms_key_id        = ""
    use_aws_owned_key = false
  }

  logs {
    general = true
    audit   = var.audit
  }

  subnet_ids = var.subnet_ids
  tags       = var.common_tags
}

# DAX

resource "aws_dax_cluster" "pass_aws_dax_cluster" {
  cluster_name       = "dax_cluster"
  node_type          = "dax.r4.large"
  subnet_group_name  = var.subnet_group
  security_group_ids = [aws_security_group.pass_dax_cluster.id]
  replication_factor = 5
  iam_role_arn       = "12345"
}

resource "aws_security_group" "pass_dax_cluster" {
  description = "Test Dax cluster"
  name        = "test_dax_cluster"
  vpc_id      = var.vpc_id
}

resource "aws_security_group_rule" "dax_cluster_ingress" {
  description       = "dax ingress rule"
  type              = "ingress"
  from_port         = 1234
  to_port           = 1234
  protocol          = "TCP"
  security_group_id = aws_security_group.pass_dax_cluster.id
}

resource "aws_security_group_rule" "dax_cluster_egress" {
  description       = "dax egress rule"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.pass_dax_cluster.id
}

# Memory DB

resource "aws_security_group" "pass_memorydb_cluster" {
  name        = "redis-secgrp"
  description = "Redis Security Group"
  vpc_id      = var.vpc_id
}

resource "aws_memorydb_cluster" "pass_memorydb_cluster" {
  acl_name           = "open-access"
  name               = "test-memorydb"
  node_type          = "db.t4g.small"
  security_group_ids = [aws_security_group.pass_memorydb_cluster.id]
  depends_on         = [aws_security_group.pass_memorydb_cluster]
}

# Route 53

resource "aws_security_group" "pass_route53_resolver_endpoint" {
  ingress {
    description = "DNS UDP"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_route53_resolver_endpoint" "pass_route53_resolver_endpoint" {
  direction          = "OUTBOUND"
  security_group_ids = [aws_security_group.pass_route53_resolver_endpoint.id]

  ip_address {
    subnet_id = var.subnet_id
  }
}

# Transfer Family

resource "aws_security_group" "pass_transfer_server" {
  ingress {
    description = "SFTP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_transfer_server" "pass_transfer_server" {
  endpoint_type = "VPC"

  endpoint_details {
    address_allocation_ids = [var.eip_id]
    subnet_ids             = [var.subnet_id]
    vpc_id                 = var.vpc_id
    security_group_ids     = [aws_security_group.pass_transfer_server.id]
  }
}
