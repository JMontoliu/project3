terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.33.0"
    }
  }
}

provider "google" {
  project = "DataIAProject3"
  region  = var.region
}