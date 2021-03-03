# Loosely from https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/autoscaling_group
locals {
  inline_map = {
    key = "a_key"
    value = "a_value"
    propagate_at_launch = false
  }
}

variable "extra_tags" {
  default = [
    {
      key                 = "Foo"
      value               = "Bar"
      propagate_at_launch = true
    },
    {
      key                 = "Baz"
      value               = "Bam"
      propagate_at_launch = true
    }
  ]
}

resource "aws_autoscaling_group" "bar" {
  name                 = "foobar3-terraform-test"
  max_size             = 5
  min_size             = 2

  tags = concat(
    [
      {
        "key"                 = "interpolation1"
        "value"               = "value3"
        "propagate_at_launch" = true
      },
      {
        "key"                 = "interpolation2"
        "value"               = "value4"
        "propagate_at_launch" = true
      },
      local.inline_map
    ],
    var.extra_tags,
  )
}

resource "aws_autoscaling_group" "bar_simplified" {
  name                 = "bar_simplified_group"
  max_size             = 5
  min_size             = 2
  tags = concat(
    [
      {
        "key"                 = "interpolation1"
        "value"               = "value3"
        "propagate_at_launch" = true
      },
      {
        "key"                 = "interpolation2"
        "value"               = "value4"
        "propagate_at_launch" = true
      }
    ]
  )
}

# From https://www.terraform.io/docs/language/functions/concat.html
locals {
  simple_list = concat(["a", ""], ["b", "c"])
  simple_list2 = concat(["a"], [""], ["b"], ["c"])
  single_item_list = concat(["a"])
  single_item_trailing_list = concat(["a"],)
}