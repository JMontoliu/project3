resource "google_storage_bucket" "terraform_state" {
  name     = var.tf_state_bucket_name
  location = var.region 
  versioning {
    enabled = true
  }
  force_destroy = false
}
