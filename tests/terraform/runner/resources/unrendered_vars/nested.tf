
variable "tags_without_component" {
  default = {
    something = "something"
  }
}

variable "tags_with_component" {
  default = {
    component = "xyz"
  }
}

variable "component" {
  default = "xyz"
}

resource "aws_s3_bucket" "unknown_nested_unknown" {
  tags = var.unknown_tags
}

resource "aws_s3_bucket" "unknown_nested_2_pass" {
  tags = {
    component = var.unknown_component
  }
}

resource "aws_s3_bucket" "known_nested_pass" {
  tags = var.tags_with_component
}

resource "aws_s3_bucket" "known_nested_2_pass" {
  tags = {
    component = var.component
  }
}

resource "aws_s3_bucket" "known_nested_fail" {
  tags = var.tags_without_component
}
