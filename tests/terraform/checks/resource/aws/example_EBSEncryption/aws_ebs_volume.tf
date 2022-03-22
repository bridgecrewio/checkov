# pass

resource "aws_ebs_volume" "enabled" {
  availability_zone = "us-west-2a"
  size              = 20

  encrypted = True
}

# fail

resource "aws_ebs_volume" "default" {
  availability_zone = "us-west-2a"
  size              = 20
}

resource "aws_ebs_volume" "disabled" {
  availability_zone = "us-west-2a"
  size              = 20

  encrypted = False
}
