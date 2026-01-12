resource "azurerm_databricks_workspace" "dxn_databricks" {
  name                = var.workspace_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "standard"

  tags = {
    purpose = "xml-processing"
    owner   = "dxn-integration"
  }
}
