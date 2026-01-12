variable "resource_group_name" {
  type        = string
  description = "Resource group for Event Hub"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "namespace_name" {
  type        = string
  description = "Event Hub namespace name"
}

variable "eventhub_name" {
  type        = string
  description = "Event Hub name"
}
