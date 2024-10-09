resource "aws_glue_connection" "example" {
  name = "example-connection"
  connection_properties = {
    for x in keys(var.connection_properties) : x => (
             startswith(each.value.connection_properties[x], "$${abcded:") 
        ? data.secret.s[split(":", trimsuffix(trimprefix(each.value.connection_properties[x], "$${abcded:"), "}"))[0]].data[split(":", trimsuffix(trimprefix(each.value.connection_properties[x], "$${vault:"), "}"))[1]]
        : each.value.connection_properties[x])
    )
  }
}

variable "connection_properties" {
  type = map(string)
  default = {
    username   = "admin"
    password   = "secret"
    database   = "mydb"
    hostname   = "example.com"
    port       = "5432"
  }
}