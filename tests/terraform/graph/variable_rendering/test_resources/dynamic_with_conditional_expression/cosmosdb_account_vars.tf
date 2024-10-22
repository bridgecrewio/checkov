variable "identity" {
  description = "The Type of Managed Identity assigned to this Cosmos account. Possible values are `SystemAssigned`, `UserAssigned` and `SystemAssigned, UserAssigned`."
  type        = any
  default = {
    type = "SystemAssigned" # Set to SystemAssigned per Cosmos THR requirement R_2.5.
  }
}
