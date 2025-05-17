module "bbdd" {
  source     = "./modules/bbdd"
  project_id = var.project_id
  bq_dataset = var.bq_dataset

  tables = [
    {
      name   = "customers"
      schema = "main.json"
    }
  ]
}

module "pubsub" {
  source = "./modules/pubsub"
  topic_name = var.topic_name
  subscription_name = var.subscription_name
  subscription_labels = var.subscription_labels
  push_endpoint = var.push_endpoint
}

module "api" {
  source                 = "./modules/api"
  project_id             = var.project_id
  region                 = var.region
  repository_name        = "docker-repo"
  image_name             = "customer-api"
  cloud_run_service_name = "customer-api"
  db_host                = "127.0.0.1" 
  port                   = "5432"
  db_name                = var.db_name
  db_user                = var.db_user
  db_password            = var.db_password
}

# module "cloud_function" {
#   source = "./module/cloud_function"
#   project_id     = var.project_id
#   region         = var.region
#   name           = "validation"
#   entry_point    = "validation_dates"
#   topic          = var.topic_hoteles
#   env_variables  = {
#     PROJECT_ID = var.project_id
#     DATASET    = var.bq_dataset
#     TABLE      = var.table_hoteles
#   }
# }