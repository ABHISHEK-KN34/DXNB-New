variable "resource_group_name" {
  type        = string
  description = "Resource group for DXN Integration"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "function_app_name" {
  type = string
}

variable "function_app_principal_id" {
  description = "Managed Identity of DXN-Integration Function App"
}

variable "function_storage_account_name" {
  type        = string
  description = "Storage account for Function runtime"
}

variable "xml_storage_account_name" {
  type        = string
  description = "Storage account for XML ingestion"
}

variable "databricks_workspace_name" {
  type        = string
  description = "Databricks workspace name"
}

variable "eventhub_namespace_name" {
  type        = string
  description = "Event Hub namespace name"
}

variable "eventhub_name" {
  type        = string
  description = "Event Hub name"
}
