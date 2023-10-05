variable "string_string" {
  description = "String var with string default"
  type        = string
  default     = "string"
}

variable "string_null" {
  description = "String var with null default"
  type        = string
  default     = null
}

resource "aws_db_instance" "default" {
  string_string = var.string_string
  string_null = var.string_null
}