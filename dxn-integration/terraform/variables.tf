variable "resource_group_name" {
  type        = string
  description = "Resource group for DXN Integration"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "function_storage_account_name" {
  type        = string
  description = "Storage account for Azure Function runtime"
}

variable "function_app_principal_id" {
  description = "Managed Identity of DXN-Integration Function App"
}

variable "function_app_name" {
  type = string
}

variable "xml_storage_account_name" {
  type        = string
  description = "Storage account name for XML ingestion"
}
variable "storage_account_name" {
  type        = string
  description = "Storage account name for general use"
}

variable "databricks_workspace_name" {
  type        = string
  description = "Databricks workspace name"
}
