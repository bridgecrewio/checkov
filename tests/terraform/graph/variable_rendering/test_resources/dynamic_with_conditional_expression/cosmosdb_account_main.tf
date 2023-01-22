# Cosmosdb account definition;
resource "azurerm_cosmosdb_account" "account" {
  # Dynamic block for configuring Cosmos account to use a specific Managed Service Identity;
  dynamic "identity" {
    for_each = length(keys(var.identity)) > 0 ? [var.identity] : []
    content {
      type         = lookup(identity.value, "type", "SystemAssigned") # Set to SystemAssigned per Cosmos THR requirement R_2.5.
      identity_ids = lookup(identity.value, "identity_ids", null)
    }
  }
}
