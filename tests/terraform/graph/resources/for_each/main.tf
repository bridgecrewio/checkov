variable "bar" {
  default = "foo"
}

resource "null_resource" "this" {
  for_each = {
    foobar = var.bar
  }
  dynamic "trigger" {
    for_each = {}
    content {}
  }
}
