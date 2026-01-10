output "function_app_name" {
  value = azurerm_linux_function_app.dxn_function.name
}

output "function_app_url" {
  value = azurerm_linux_function_app.dxn_function.default_hostname
}
