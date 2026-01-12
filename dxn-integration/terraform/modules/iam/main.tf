# Databricks → XML Storage (Read)
resource "azurerm_role_assignment" "function_eventhub_sender" {
  scope                = var.eventhub_namespace_id
  role_definition_name = "Azure Event Hubs Data Sender"
  principal_id         = var.function_principal_id
  principal_type       = "ServicePrincipal"
}


# DXN-Integration → Event Hub (Send)
#resource "azurerm_role_assignment" "function_eventhub_sender" {
#  scope                = var.eventhub_namespace_id
#  role_definition_name = "Azure Event Hubs Data Sender"
#  principal_id         = var.function_principal_id
#}