locals {
  a     = "a"
  b     = "b"
  empty = ""

  bool_true  = true ? "correct" : "wrong"
  bool_false = false ? "wrong" : "correct"

  bool_string_true  = "true" ? "correct" : "wrong"
  bool_string_false = "false" ? "wrong" : "correct"

  compare_string_true  = "a" == "a" ? "correct" : "wrong"
  compare_string_false = "a" != "a" ? "wrong" : "correct"

  compare_num_true  = 1 == 1 ? "correct" : "wrong"
  compare_num_false = 1 != 1 ? "correct" : "wrong"

  # NOTE: I don't think evals in locals is valid in TF, but the parser will eval it
  default_not_taken = local.a != "" ? local.a : "default value"
  default_taken     = local.empty != "" ? local.a : "default value"

  type        = bool
  default     = true
  description = "Whether or not the metadata service requires session tokens"
}

resource "aws_instance" "foo" {
  ami           = "ami-005e54dee72cc1d00" # us-west-2
  instance_type = "t2.micro"

  root_block_device {
    encrypted = true
  }

  metadata_options {
    http_tokens = (var.metadata_http_tokens_required) ? "required" : "optional"
  }
}