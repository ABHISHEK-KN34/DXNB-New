# -------------------------
# RESOURCE GROUP
# -------------------------
resource "azurerm_resource_group" "dxn_rg" {
  name     = var.resource_group_name
  location = var.location
}

# -------------------------
# FUNCTION RUNTIME STORAGE
# -------------------------
resource "azurerm_storage_account" "function_sa" {
  name                     = var.function_storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
}

# -------------------------
# STORAGE MODULE (XML)
# -------------------------
module "storage" {
  source               = "./modules/storage"
  resource_group_name  = var.resource_group_name
  location             = var.location
  storage_account_name = var.xml_storage_account_name
}

# -------------------------
# DATABRICKS MODULE
# -------------------------
module "databricks" {
  source              = "./modules/databricks"
  resource_group_name = var.resource_group_name
  location            = var.location
  workspace_name      = var.databricks_workspace_name
}

# -------------------------
# EVENT HUB MODULE
# -------------------------
module "eventhub" {
  source              = "./modules/eventhub"
  resource_group_name = var.resource_group_name
  location            = var.location
  namespace_name      = var.eventhub_namespace_name
  eventhub_name       = var.eventhub_name
}

# -------------------------
# APP SERVICE PLAN
# -------------------------
resource "azurerm_service_plan" "function_plan" {
  name                = "asp-dxnb-new-dev"
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = "Y1"
}

# -------------------------
# AZURE FUNCTION APP
# -------------------------
resource "azurerm_linux_function_app" "dxn_function" {
  name                = var.function_app_name
  resource_group_name = var.resource_group_name
  location            = var.location

  service_plan_id     = azurerm_service_plan.function_plan.id
  storage_account_name       = azurerm_storage_account.function_sa.name
  storage_account_access_key = azurerm_storage_account.function_sa.primary_access_key

  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME = "python"
    WEBSITE_RUN_FROM_PACKAGE = "1"
  }
}

# -------------------------
# IAM MODULE (ONLY FUNCTION → EVENT HUB)
# -------------------------
module "iam" {
  source                = "./modules/iam"
  storage_account_id    = module.storage.storage_account_id
  eventhub_namespace_id = module.eventhub.namespace_id
  function_principal_id = var.function_app_principal_id
}

