resource "azurerm_storage_account" "xml_storage" {
  name                = var.storage_account_name
  resource_group_name = var.resource_group_name
  location            = var.location

  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  tags = {
    purpose = "xml-ingestion"
    owner   = "dxn-integration"
  }
}

resource "azurerm_storage_container" "xml_container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.xml_storage.name
  container_access_type = "private"
}
