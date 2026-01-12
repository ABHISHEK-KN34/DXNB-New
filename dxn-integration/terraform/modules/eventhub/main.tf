resource "azurerm_eventhub_namespace" "dxn_namespace" {
  name                = var.namespace_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
  capacity            = 1

  tags = {
    purpose = "dxn-events"
    owner   = "dxn-integration"
  }
}

resource "azurerm_eventhub" "dxn_eventhub" {
  name                = var.eventhub_name
  namespace_name      = azurerm_eventhub_namespace.dxn_namespace.name
  resource_group_name = var.resource_group_name
  partition_count     = 2
  message_retention   = 1
}

resource "azurerm_eventhub_authorization_rule" "dxn_send_rule" {
  name                = "dxn-send"
  namespace_name      = azurerm_eventhub_namespace.dxn_namespace.name
  eventhub_name       = azurerm_eventhub.dxn_eventhub.name
  resource_group_name = var.resource_group_name

  send   = true
  listen = false
  manage = false
}
