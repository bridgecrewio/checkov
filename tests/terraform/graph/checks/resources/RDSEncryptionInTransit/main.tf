# Unknown: aws_db_instance with no connection
resource "aws_db_instance" "pass_no_param" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.notexist.name
  apply_immediately    = true
}

# Pass: aws_db_parameter_group with no connection
resource "aws_db_parameter_group" "no_connect" {
  name   = "my-pg"
  family = "db2-ae"

  parameter {
    name  = "db2comm"
    value = "0"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Pass: Postgres with rds.force_ssl set to 1
resource "aws_db_instance" "postgres_pass1" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.postgres_pass.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "postgres_pass" {
  name   = "my-pg"
  family = "postgres13"

  parameter {
    name  = "something_else"
    value = "0"
  }

  parameter {
    name  = "rds.force_ssl"
    value = "1" # Must exist and must be 1
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Fail: Postgres with rds.force_ssl set to 1
resource "aws_db_instance" "postgres_fail1" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.postgres_fail_0.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "postgres_fail_0" {
  name   = "my-pg"
  family = "postgres13"

  parameter {
    name  = "something_else"
    value = "0"
  }

  parameter {
    name  = "rds.force_ssl"
    value = "0" # Must exist and must be 1
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Fail: Postgres with rds.force_ssl set to 1
resource "aws_db_instance" "postgres_fail_missing" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.postgres_fail_missing.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "postgres_fail_missing" {
  name   = "my-pg"
  family = "postgres13"

  parameter {
    name  = "something_else"
    value = "0"
  }

  lifecycle {
    create_before_destroy = true
  }
}


# Pass: Postgres with rds.force_ssl set to 1
resource "aws_db_instance" "pass_other_fam" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.pass_other_fam.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "pass_other_fam" {
  name   = "my-pg"
  family = "other-fam"

  parameter {
    name  = "something_else"
    value = "0"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Fail: mariadb require_secure_transport set to 0
resource "aws_db_instance" "maria_fail_0" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.maria_fail_0.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "maria_fail_0" {
  name   = "my-pg"
  family = "mariadb1"

  parameter {
    name  = "require_secure_transport"
    value = "0"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Pass: mariadb require_secure_transport set to 1
resource "aws_db_instance" "mariadb_pass" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.mariadb_pass.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "mariadb_pass" {
  name   = "my-pg"
  family = "mariadb1"

  parameter {
    name  = "something_else"
    value = "1"
  }

  parameter {
    name  = "require_secure_transport"
    value = "1"
  }

  parameter {
    name  = "something_else2"
    value = "1"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Pass: mariadb require_secure_transport set to 1
resource "aws_db_instance" "mariadb_fail_missing" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.mariadb_fail_missing.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "mariadb_fail_missing" {
  name   = "my-pg"
  family = "mariadb1"

  parameter {
    name  = "something_else"
    value = "1"
  }

  parameter {
    name  = "something_else2"
    value = "1"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Fail: db2 with db2comm set to 0
resource "aws_db_instance" "db2_fail_0" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.db2_fail_0.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "db2_fail_0" {
  name   = "my-pg"
  family = "1db2-ae1"

  parameter {
    name  = "db2comm"
    value = "0"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Pass: db2 with db2comm set to SSL
resource "aws_db_instance" "db2_pass" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.db2_pass.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "db2_pass" {
  name   = "my-pg"
  family = "1db2-ae1"

  parameter {
    name  = "db2comm"
    value = "SSL"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Fail: db2 with db2comm missing
resource "aws_db_instance" "db2_fail_missing" {
  # other attributes
  parameter_group_name = aws_db_parameter_group.db2_fail_missing.name
  apply_immediately    = true
}

resource "aws_db_parameter_group" "db2_fail_missing" {
  name   = "my-pg"
  family = "1db2-ae1"

  lifecycle {
    create_before_destroy = true
  }
}
