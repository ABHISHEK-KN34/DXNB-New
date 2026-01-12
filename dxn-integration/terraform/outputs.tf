output "function_app_name" {
  value = var.function_app_name
}

output "function_app_url" {
  value = "${var.function_app_name}.azurewebsites.net"
}

output "storage_account_name" {
  value = module.storage.storage_account_name
}
