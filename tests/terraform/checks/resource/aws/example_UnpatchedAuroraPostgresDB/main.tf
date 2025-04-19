resource "aws_db_instance" "fail1" {
  # Vulnerable Aurora PostgreSQL instance
  allocated_storage = 10
  apply_immediately  = true
  auto_minor_version_upgrade = true
  availability_zone = "us-east-1a"
  db_name            = "vulnerable_db"
  db_subnet_group_name = "default"
  engine             = "aurora-postgresql"
  engine_version     = "10.12" # Vulnerable version
  identifier         = "vulnerable-aurora-instance"
  instance_class     = "db.t3.micro"
  monitoring_interval = 5
  multi_az           = false
  password           = "password123"
  port               = 5432
  storage_type       = "gp2"
  username           = "admin"
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  # Enable the vulnerable 'log_fdw' extension
  # This is the key vulnerability
  enabled_cloudwatch_logs_exports = ["error", "audit"]
  engine_parameters {
    name  = "log_fdw"
    value = "on"
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "default"
  subnet_ids = [aws_subnet.public1.id]
}

resource "aws_security_group" "db_sg" {
  name        = "db-sg"
  description = "Security group for Aurora PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_db_instance" "pass" {
  # Safe Aurora PostgreSQL instance
  allocated_storage = 10
  apply_immediately  = true
  auto_minor_version_upgrade = true
  availability_zone = "us-east-1a"
  db_name            = "safe_db"
  db_subnet_group_name = "default"
  engine             = "aurora-postgresql"
  engine_version     = "11.10" # Safe version (latest for now)
  identifier         = "safe-aurora-instance"
  instance_class     = "db.t3.micro"
  monitoring_interval = 5
  multi_az           = false
  password           = "password123"
  port               = 5432
  storage_type       = "gp2"
  username           = "admin"
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  # Disable the 'log_fdw' extension
  # This is the key mitigation
  enabled_cloudwatch_logs_exports = ["error", "audit"]
  engine_parameters {
    name  = "log_fdw"
    value = "off"
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "default"
  subnet_ids = [aws_subnet.public1.id]
}

resource "aws_security_group" "db_sg" {
  name        = "db-sg"
  description = "Security group for Aurora PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_db_instance" "fail2" {
  # Vulnerable Aurora PostgreSQL instance
  allocated_storage = 10
  apply_immediately  = true
  auto_minor_version_upgrade = true
  availability_zone = "us-east-1a"
  db_name            = "vulnerable_db"
  db_subnet_group_name = "default"
  engine             = "aurora-postgresql"
  engine_version     = "11.8" # Vulnerable version
  identifier         = "vulnerable-aurora-instance"
  instance_class     = "db.t3.micro"
  monitoring_interval = 5
  multi_az           = false
  password           = "password123"
  port               = 5432
  storage_type       = "gp2"
  username           = "admin"
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  # Enable the vulnerable 'log_fdw' extension
  # This is the key vulnerability
  enabled_cloudwatch_logs_exports = ["error", "audit"]
  engine_parameters {
    name  = "log_fdw"
    value = "on"
  }
}