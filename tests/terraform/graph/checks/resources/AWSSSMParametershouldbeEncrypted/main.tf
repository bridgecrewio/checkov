resource "aws_ssm_parameter" "aws_ssm_parameter_ok" {
 name            = "sample"
 type            = "SecureString"
 value           = "test"
 description     = "policy test"
 tier            = "Standard"
 allowed_pattern = ".*"
 data_type       = "text"
}

resource "aws_ssm_parameter" "aws_ssm_parameter_not_ok" {
 name            = "sample"
 type            = "String"
 value           = "test"
 description     = "policy test"
 tier            = "Standard"
 allowed_pattern = ".*"
 data_type       = "text"
}