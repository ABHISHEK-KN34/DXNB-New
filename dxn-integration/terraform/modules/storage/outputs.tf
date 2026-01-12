output "storage_account_name" {
  value = azurerm_storage_account.xml_storage.name
}

output "storage_account_id" {
  value = azurerm_storage_account.xml_storage.id
}

output "container_name" {
  value = azurerm_storage_container.xml_container.name
}
