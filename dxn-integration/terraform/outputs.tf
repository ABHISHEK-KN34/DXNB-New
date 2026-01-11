output "function_app_name" {
  value = azurerm_linux_function_app.dxn_function.name
}

output "function_app_url" {
  value = azurerm_linux_function_app.dxn_function.default_hostname
}

output "storage_account_name" {
  value = module.storage.storage_account_name
}

output "databricks_workspace_url" {
  value = module.databricks.workspace_url
}

output "eventhub_name" {
  value = module.eventhub.eventhub_name
}
