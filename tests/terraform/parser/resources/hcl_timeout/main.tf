resource "aws_glue_connection" "example" {
  name = "example-connection"
  connection_properties = {
             startswith(each.value.connection_properties[x], "$${abcded:"


variable "connection_properties" {

}