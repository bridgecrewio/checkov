resource "aws_instance" "web" {
  ami               = "ami-21f78e11"
  availability_zone = "us-west-2a"
  instance_type     = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}

resource "aws_volume_attachment" "not_ok_attachment1" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.not_ok_ebs1.id
  instance_id = aws_instance.web.id
}

resource "aws_volume_attachment" "not_ok_attachment2" {
  device_name = "/dev/sdh2"
  volume_id   = aws_ebs_volume.not_ok_ebs2.id
  instance_id = aws_instance.web.id
}

resource "aws_volume_attachment" "ok_attachment1" {
  device_name = "/dev/sdh3"
  volume_id   = aws_ebs_volume.ok_ebs2.id
  instance_id = aws_instance.web.id
}

resource "aws_ebs_volume" "not_ok_ebs1" {
  availability_zone = ""
}

resource "aws_ebs_volume" "not_ok_ebs2" {
  availability_zone = ""
  encrypted = false
}

resource "aws_ebs_volume" "ok_ebs1" {
  availability_zone = ""
}

resource "aws_ebs_volume" "ok_ebs2" {
  availability_zone = ""
  encrypted = true
}


resource "aws_volume_attachment" "ebs_at1" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.not_ok_ebs1.id
  instance_id = aws_instance.web.id
}