module "bucket-state" {
  source = "./modules/bucket-state"
  tf_state_bucket_name = var.tf_state_bucket_name
  region = var.region
}

module "bbdd" {
  source = "./modules/bbdd"
  region = var.region
  name_instance_bbdd = var.name_instance_bbdd
  db_tier = var.db_tier
  db_version = var.db_version
  db_name = var.db_name
  db_user = var.db_user
  db_password = var.db_password
}

module "pubsub" {
  source = "./modules/pubsub"
  topic_name = var.topic_name
  subscription_name = var.subscription_name
  subscription_labels = var.subscription_labels
  push_endpoint = var.push_endpoint
}