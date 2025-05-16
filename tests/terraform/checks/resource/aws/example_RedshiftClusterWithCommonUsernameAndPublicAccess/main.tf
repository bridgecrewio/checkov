provider "aws" {
  region = "us-west-2"
}

resource "aws_redshift_cluster" "fail" {
  cluster_identifier  = "vulnerable-redshift-cluster"
  database_name      = "productiondb"
  master_username    = "administrator"
  master_password    = "Complex-P@ssw0rd789"
  node_type          = "dc2.large"
  cluster_type       = "single-node"

  publicly_accessible = true

  skip_final_snapshot = true

  vpc_security_group_ids = [aws_security_group.redshift_sg.id]
}

resource "aws_security_group" "redshift_sg" {
  name        = "vulnerable-redshift-sg"
  description = "Security group for vulnerable Redshift cluster"

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_redshift_cluster" "pass1" {
  cluster_identifier  = "safe-redshift-cluster"
  database_name      = "productiondb"
  master_username    = "custom_user_84629"
  master_password    = "vK#9mP$2nL@5qR8x"
  node_type          = "dc2.large"
  cluster_type       = "single-node"

  publicly_accessible = false

  skip_final_snapshot = true

  vpc_security_group_ids = [aws_security_group.safe_redshift_sg.id]

  encrypted           = true
  kms_key_id         = aws_kms_key.redshift_key.arn
}

resource "aws_kms_key" "redshift_key" {
  description = "KMS key for Redshift cluster encryption"
  enable_key_rotation = true
}

resource "aws_security_group" "safe_redshift_sg" {
  name        = "safe-redshift-sg"
  description = "Security group for safe Redshift cluster"

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # Restricted to internal VPC CIDR
  }
}

resource "aws_redshift_cluster" "pass2" {
  cluster_identifier  = "vulnerable-redshift-cluster"
  database_name      = "productiondb"
  master_username    = "administrator"
  master_password    = "Complex-P@ssw0rd789"
  node_type          = "dc2.large"
  cluster_type       = "single-node"

  publicly_accessible = false

  skip_final_snapshot = true

  vpc_security_group_ids = [aws_security_group.redshift_sg.id]
}

resource "aws_redshift_cluster" "pass3" {
  cluster_identifier  = "vulnerable-redshift-cluster"
  database_name      = "productiondb"
  master_username    = "adm1n1str@t0r"
  master_password    = "Complex-P@ssw0rd789"
  node_type          = "dc2.large"
  cluster_type       = "single-node"

  publicly_accessible = true

  skip_final_snapshot = true

  vpc_security_group_ids = [aws_security_group.redshift_sg.id]
}