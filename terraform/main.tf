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
      name   = "reservas"
      schema = "main.json"
    },
    {
    name   = "clients"
    schema = "clients.json"
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

}

module "web_streamlit" {
  source                     = "./modules/web_streamlit"
  project_id                 = var.project_id
  region                     = var.region
  repository_name4           = var.repository_name4
  image_name4                = var.image_name4
  cloud_run_service_name4    = var.cloud_run_service_name4
  url_chatbot2                = module.chatbot.url_chatbot


}


module "injectors" {
  source          = "./modules/injectors"
  project_id      = var.project_id
  region          = var.region
  api_url         = module.api.api_url
  chatbot         = module.chatbot.env_vars_api
  chatbot_url     = module.chatbot.url_chatbot
  streamlit       = module.web_streamlit.streamlit_name

  depends_on = [ module.api, module.chatbot, module.web_streamlit ]

}

module "cloud_function" {
  name        = "cloud_function"
  source      = "./modules/cloud_function"
  project_id  = var.project_id
  region      = var.region
  entry_point = var.entry_point
  topic       = var.topic

  env_variables = {
    # BigQuery
    PROJECT_ID = var.project_id
    DATASET    = var.bq_dataset
    REGION   = var.region


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
