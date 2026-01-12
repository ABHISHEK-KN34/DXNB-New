variable "resource_group_name" {
  type        = string
  description = "Resource group name"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "storage_account_name" {
  type        = string
  description = "Unique storage account name"
}

variable "container_name" {
  type        = string
  default     = "xml-input"
}
