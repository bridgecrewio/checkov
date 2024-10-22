variable "dynamic" {
 description = "TODO"
  type = object({
          outbound_ports  = list(string)
          inbound_ports   = list(string)
    })
}