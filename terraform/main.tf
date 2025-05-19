module "bbdd" {
  source     = "./modules/bbdd"
  project_id = var.project_id
  bq_dataset = var.bq_dataset
  region               = var.region
  postgres_instance_name = var.postgres_instance_name
  postgres_tier        = var.postgres_tier
  postgres_db_name     = var.db_name
  postgres_user        = var.db_user  
  postgres_password    = var.db_password
  

  tables = [
    {
      name   = "customers"
      schema = "main.json"
    }
  ]
}

module "api" {
  source                 = "./modules/api"
  project_id             = var.project_id
  region                 = var.region
  repository_name        = "docker-repo"
  image_name             = "customer-api"
  cloud_run_service_name = "customer-api"
  db_host                = module.bbdd.sql_host
  port                   = "5432"
  db_name                = var.db_name
  db_user                = var.db_user
  db_password            = var.db_password

  depends_on = [ module.bbdd, module.cloud_function ]
}

module "chatbot" {
  source                    = "./modules/chatbot"
  project_id                = var.project_id
  region                    = var.region
  repository_name2           = var.repository_name2
  image_name2                = var.image_name2
  cloud_run_service_name2    = var.cloud_run_service_name2
  url_api                   = module.api.api_url
  google_api_key          = var.google_api_key
  api_weather_key         = var.api_weather_key


  depends_on = [ module.api, module.bbdd, module.cloud_function ]
}

module "telegram" {
  source                     = "./modules/telegram"
  project_id                 = var.project_id
  region                     = var.region
  repository_name3           = var.repository_name3
  image_name3                = var.image_name3
  cloud_run_service_name3    = var.cloud_run_service_name3
  url_chatbot                = module.chatbot.url_chatbot
  telegram_api_key           = var.telegram_api_key

  depends_on = [ module.chatbot]
}


# module "injectors" {
#   source          = "./modules/injectors"
#   project_id      = var.project_id
#   region          = var.region
#   api_url         = module.api.api_url
#   chatbot         = module.chatbot.env_vars_api

#   depends_on = [ module.api, module.bbdd, module.chatbot ]
# }

module "cloud_function" {
  name        = "cloud_function"
  source      = "./modules/cloud_function"
  project_id  = var.project_id
  region      = var.region
  entry_point = var.entry_point
  topic       = var.topic

  env_variables = {
    # BigQuery
    # PROJECT_ID = var.project_id
    # DATASET    = var.bq_dataset
    # TABLES =  "customers"


    # PostgreSQL
    PG_HOST     = module.bbdd.sql_host
    PG_PORT     = var.port 
    PG_USER     = var.db_user
    PG_PASSWORD = var.postgres_password
    PG_DATABASE = var.postgres_db_name

    # Logging
    LOG_LEVEL   = "INFO"
  }
  depends_on = [ module.bbdd ]
}
