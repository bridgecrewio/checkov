variable "public_nacl_inbound_tcp_ports" {
  type        = list(string)
  default     = ["80", "443", "22", "1194"]
  description = "TCP Ports to allow inbound on public subnet via NACLs (this list cannot be empty)"
}