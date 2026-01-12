variable "storage_account_id" {
  description = "ID of XML storage account"
  type        = string
}

variable "eventhub_namespace_id" {
  description = "ID of Event Hub namespace"
  type        = string
}

#variable "databricks_principal_id" {
#  description = "Managed identity of Databricks workspace"
#  type        = string
#}

variable "function_principal_id" {
  description = "Managed identity of DXN-Integration Function App"
  type        = string
}
