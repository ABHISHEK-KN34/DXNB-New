output "eventhub_name" {
  value = azurerm_eventhub.dxn_eventhub.name
}

output "namespace_name" {
  value = azurerm_eventhub_namespace.dxn_namespace.name
}

output "send_connection_string" {
  value = azurerm_eventhub_authorization_rule.dxn_send_rule.primary_connection_string
  sensitive = true
}

output "namespace_id" {
  value = azurerm_eventhub_namespace.dxn_namespace.id
}
