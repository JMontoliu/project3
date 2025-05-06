terraform {
  backend "gcs" {
    bucket = "tfstate_project3"
    prefix = "terraform/state"
  }
}

module "pubsub" {
  source     = "./modules/pubsub"
  project_id = var.project_id
  topics     = ["customes"]
}

module "database" {
  source     = "./modules/database"
  project_id = var.project_id
  location   = "europe-southwest1"
}
