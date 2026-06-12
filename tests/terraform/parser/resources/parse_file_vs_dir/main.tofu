# Do not add more files to this directory.

resource "aws_elb" "learn" {
  instances = aws_instance.ubuntu[*].id
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400
  listener {
    instance_port     = 0
    instance_protocol = ""
    lb_port           = 0
    lb_protocol       = ""
  }
}

resource "aws_elb" "learn1" {
  instances = aws_instance.ubuntu[*].id
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400
  listener {
    instance_port     = 0
    instance_protocol = ""
    lb_port           = 0
    lb_protocol       = ""
  }
}

resource "aws_elb" "learn2" {
  instances = aws_instance.ubuntu[*].id
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400
  listener {
    instance_port     = 0
    instance_protocol = ""
    lb_port           = 0
    lb_protocol       = ""
  }
}
