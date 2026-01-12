# =========================
# Core DXN-Integration Infra (Phase 1)
# =========================
resource "azurerm_storage_account" "function_sa" {
  name                     = var.function_storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  tags = {
    purpose = "function-runtime"
  }
}

resource "azurerm_resource_group" "dxn_rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_service_plan" "dxn_plan" {
  name                = "asp-dxnb-new"
  resource_group_name = azurerm_resource_group.dxn_rg.name
  location            = azurerm_resource_group.dxn_rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_function_app" "dxn_function" {
  name                = var.function_app_name
  resource_group_name = azurerm_resource_group.dxn_rg.name
  location            = azurerm_resource_group.dxn_rg.location
  service_plan_id     = azurerm_service_plan.dxn_plan.id
  storage_account_name       = azurerm_storage_account.function_sa.name
  storage_account_access_key = azurerm_storage_account.function_sa.primary_access_key


  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME = "python"
  }
}

# =========================
# Phase 2 Infra (Module-Driven)
# =========================

module "storage" {
  source               = "./modules/storage"
  resource_group_name  = var.resource_group_name
  location             = var.location
  storage_account_name = var.xml_storage_account_name
}

module "databricks" {
  source              = "./modules/databricks"
  resource_group_name = var.resource_group_name
  location            = var.location
  workspace_name      = var.databricks_workspace_name
}


#module "eventhub" {
#  source              = "./modules/eventhub"
#  resource_group_name = var.resource_group_name
#  location            = var.location
#}

#module "iam" {
#  source                 = "./modules/iam"
#  resource_group_name    = var.resource_group_name
#  storage_account_id     = module.storage.storage_account_id
#  eventhub_namespace_id  = module.eventhub.namespace_id
#  databricks_principal   = module.databricks.workspace_principal_id
#  function_principal     = azurerm_linux_function_app.dxn_function.identity[0].principal_id
#}
