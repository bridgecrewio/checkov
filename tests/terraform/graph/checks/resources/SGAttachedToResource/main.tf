# pass

# Batch

resource "aws_security_group" "pass_batch" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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

# DMS

resource "aws_security_group" "pass_dms" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_dms_replication_instance" "pass_dms" {
  replication_instance_class = "dms.t3.micro"
  replication_instance_id    = "dms"
  vpc_security_group_ids     = [aws_security_group.pass_dms.id]
}

# DocDB

resource "aws_security_group" "pass_docdb" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_instance" "pass_ec2" {
  ami           = "data.aws_ami.ubuntu.id"
  instance_type = "t3.micro"
  security_groups = [aws_security_group.pass_ec2.id]
}

resource "aws_security_group" "pass_ec2_client_vpn" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_launch_template" "pass_ec2_launch_template" {
  image_id               = "data.aws_ami.ubuntu.id"
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.pass_ec2_launch_template.id]
}

# ECS

resource "aws_security_group" "pass_ecs" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_elasticache_cluster" "pass_elasticache" {
  cluster_id         = "cache"
  security_group_ids = [aws_security_group.pass_elasticache.id]
}

# ELB

resource "aws_security_group" "pass_alb" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_lb" "pass_lb" {
  load_balancer_type = "application"
  security_groups    = [aws_security_group.pass_lb.id]
}

# ENI

resource "aws_security_group" "pass_eni" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_elasticsearch_domain" "pass_es" {
  domain_name = "es"

  vpc_options {
    security_group_ids = [aws_security_group.pass_es.id]
  }
}

# Lambda

resource "aws_security_group" "pass_lambda" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_neptune_cluster" "pass_neptune" {
  vpc_security_group_ids = [aws_security_group.pass_neptune.id]
}

# RDS

resource "aws_security_group" "pass_rds" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
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
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_vpc_endpoint" "pass_vpc_endpoint" {
  vpc_id             = "aws_vpc.this.id"
  service_name       = "com.amazonaws.us-west-2.s3"
  vpc_endpoint_type  = "Interface"
  security_group_ids = [aws_security_group.pass_vpc_endpoint.id]
}

# fail

resource "aws_security_group" "fail" {
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = 0.0.0.0/0
  }
}

resource "aws_emr_cluster" "pass_emr" {
  name                   = var.cluster_name
  release_label          = var.release_label
  security_configuration = aws_emr_security_configuration.examplea.name

  ec2_attributes {
    subnet_id                         = var.subnet_id
    emr_managed_master_security_group = aws_security_group.pass_emr.id
    emr_managed_slave_security_group  = aws_security_group.pass_emr.id
    instance_profile                  = aws_iam_instance_profile.examplea.arn
  }

  service_role = aws_iam_role.emr_service.arn
}

resource "aws_security_group" "pass_emr" {
  //todo
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

resource "aws_cloudwatch_event_target" "pass_cloudwatch_event" {
  target_id = var.target_id
  arn       = var.arn
  rule      = var.rule
  role_arn  = var.role_arn

  ecs_target {
    launch_type = var.launch_type
    task_count  = var.task_count
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
