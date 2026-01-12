variable "resource_group_name" {
  type        = string
  description = "Resource group for Databricks workspace"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "workspace_name" {
  type        = string
  description = "Databricks workspace name"
}
