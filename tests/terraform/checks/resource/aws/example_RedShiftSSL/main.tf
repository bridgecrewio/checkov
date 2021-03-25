
resource "aws_redshift_parameter_group" "failasfalse" {
  name   = var.param_group_name
  family = "redshift-1.0"

  parameter {
    name  = "require_ssl"
    value = "false"
  }

  parameter {
    name  = "enable_user_activity_logging"
    value = "true"
  }
}


resource "aws_redshift_parameter_group" "fail" {
  name   = var.param_group_name
  family = "redshift-1.0"

}


resource "aws_redshift_parameter_group" "pass" {
  name   = var.param_group_name
  family = "redshift-1.0"

  parameter {
    name  = "require_ssl"
    value = "true"
  }

  parameter {
    name  = "enable_user_activity_logging"
    value = "true"
  }
}

resource "aws_redshift_parameter_group" "passbutbool" {
  name   = var.param_group_name
  family = "redshift-1.0"

  parameter {
    name  = "require_ssl"
    value = true
  }

  parameter {
    name  = "enable_user_activity_logging"
    value = "true"
  }
}