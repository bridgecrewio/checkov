resource "aws_instance" "defaults" {
  metadata_options {
  }
}

resource "aws_instance" "optional_token" {
  metadata_options {
    http_endpoint               = "enabled"
    http_put_response_hop_limit = "1"
    http_tokens                 = "optional"
  }
}

resource "aws_instance" "disabled" {
  metadata_options {
    http_endpoint = "disabled"
  }
}

resource "aws_instance" "required" {
  metadata_options {
    http_tokens = "required"
  }
}

resource "aws_launch_configuration" "required_lc" {
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
  image_id      = ""
  instance_type = ""
}

resource "aws_launch_configuration" "optional_lc" {
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"
  }
  image_id      = ""
  instance_type = ""
}

resource "aws_launch_template" "optional_lt" {
  metadata_options {
    http_tokens = "optional"
  }
}

resource "aws_launch_template" "default_lt" {
  metadata_options {
    http_endpoint = "enabled"
  }
}