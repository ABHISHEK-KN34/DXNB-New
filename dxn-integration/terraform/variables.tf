variable "resource_group_name" {
  type        = string
  description = "Resource group for DXN Integration"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "function_app_name" {
  type        = string
}

variable "storage_account_name" {
  type        = string
}
