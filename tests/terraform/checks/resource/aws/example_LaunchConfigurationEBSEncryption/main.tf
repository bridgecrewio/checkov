resource "aws_instance" "fail" {
  image_id      = "ami-123"
  instance_type = "t2.micro"
  root_block_device {
    encrypted = False
  }
}

resource "aws_instance" "fail2" {
  image_id      = "ami-123"
  instance_type = "t2.micro"
  root_block_device {}
}

resource "aws_instance" "fail3" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
    encrypted   = true
  }


  ebs_block_device {
    volume_type = "gp2"
    volume_size = var.ebs_volume_size
    device_name = "/dev/xvdb"
    encrypted   = false
  }
}

resource "aws_instance" "fail4" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  ebs_block_device {
    volume_type = "gp2"
    volume_size = var.ebs_volume_size
    device_name = "/dev/xvdb"
    encrypted   = false
  }
}

resource "aws_instance" "fail5" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name
}

# empty array defaults

variable "empty_list" {
  default = []
}

resource "aws_instance" "fail_empty_root_list" {
  image_id      = "ami-123"
  instance_type = "t2.micro"

  root_block_device = var.empty_list
}

resource "aws_instance" "unknown_empty_ebs_list" {
  image_id      = "ami-123"
  instance_type = "t2.micro"

  root_block_device = {
    volume_type = "gp2"
    volume_size = var.root_volume_size
    encrypted   = true
  }

  ebs_block_device = var.empty_list
}

# pass

resource "aws_instance" "pass" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
    snapshot_id = "snap-1234"
  }
}
resource "aws_instance" "pass2" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
    encrypted   = true
  }
}

resource "aws_instance" "pass3" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  ebs_block_device {
    volume_type = "gp2"
    volume_size = var.ebs_volume_size
    device_name = "/dev/xvdb"
    encrypted   = true
  }

  root_block_device {
    volume_type = "gp2"
    volume_size = var.root_volume_size
    encrypted   = true
  }

}

resource "aws_launch_configuration" "pass" {
  name_prefix                 = "elk"
  image_id                    = data.aws_ami.elk.image_id
  iam_instance_profile        = aws_iam_instance_profile.elk.name
  instance_type               = var.instance_type
  security_groups             = [aws_security_group.elk.id]
  associate_public_ip_address = false

  lifecycle {
    create_before_destroy = true
  }

  root_block_device {
    encrypted = var.encrypted
  }
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
}

resource "aws_launch_configuration" "pass2" {
  name_prefix                 = "elk"
  image_id                    = data.aws_ami.elk.image_id
  iam_instance_profile        = aws_iam_instance_profile.elk.name
  instance_type               = var.instance_type
  security_groups             = [aws_security_group.elk.id]
  associate_public_ip_address = false

  lifecycle {
    create_before_destroy = true
  }

  root_block_device {
    encrypted = var.encrypted
  }

  ephemeral_block_device {
    device_name  = "somedisk"
    virtual_name = "fred"
  }

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
}

resource "aws_launch_configuration" "fail" {
  name_prefix                 = "elk"
  image_id                    = data.aws_ami.elk.image_id
  iam_instance_profile        = aws_iam_instance_profile.elk.name
  instance_type               = var.instance_type
  security_groups             = [aws_security_group.elk.id]
  associate_public_ip_address = false

  lifecycle {
    create_before_destroy = true
  }

  root_block_device {
    encrypted = false
  }
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
}

variable "encrypted" {
  description = "Root block device encryption"
  type        = bool
  default     = true
}