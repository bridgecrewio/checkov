# pass

# EC2 instance

resource "aws_instance" "default" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}

resource "aws_instance" "private" {
  ami           = "ami-12345"
  instance_type = "t3.micro"

  associate_public_ip_address = false
}

# launch template

resource "aws_launch_template" "default" {
  image_id      = "ami-12345"
  instance_type = "t3.micro"
}

resource "aws_launch_template" "private" {
  image_id      = "ami-12345"
  instance_type = "t3.micro"

  network_interfaces {
    associate_public_ip_address = false
  }
}

# fail

# EC2 instance

resource "aws_instance" "public" {
  ami           = "ami-12345"
  instance_type = "t3.micro"

  associate_public_ip_address = true
}

# launch template

resource "aws_launch_template" "public" {
  image_id      = "ami-12345"
  instance_type = "t3.micro"

  network_interfaces {
    associate_public_ip_address = true
  }
}

variable "public" {
  default = {
    "key1": true,
    "key2": false
  }
}

resource "aws_instance" "public_foreach" {
  for_each = var.public
  ami           = "ami-12345"
  instance_type = "t3.micro"

  associate_public_ip_address = each.value
}

variable "public_loop" {
  default = [{
    "name": "key3",
  },
  {
    "name": "key4",
  }]
}

variable "loop_list" {
  default = ["k", "v"]
}

resource "aws_instance" "public_foreach_loop" {
  for_each = { for val in var.public_loop : val.name => true }
  ami           = "ami-12345"
  instance_type = "t3.micro"

  associate_public_ip_address = each.value
}

resource "aws_instance" "public_foreach_loop_list" {
  for_each = [ for val in var.loop_list : val ]
  ami           = "ami-12345"
  instance_type = "t3.micro"
  associate_public_ip_address = each.value
}

