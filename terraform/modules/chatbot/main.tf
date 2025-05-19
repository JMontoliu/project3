resource "google_artifact_registry_repository" "repo" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_name2
  format        = "DOCKER"
}

# Autenticación con Artifact Registry
resource "null_resource" "docker_auth" {
  provisioner "local-exec" {
    command = "gcloud auth configure-docker ${var.region}-docker.pkg.dev"
  }

  depends_on = [google_artifact_registry_repository.repo]
}

# Construcción de la imagen con Docker y push a Artifact Registry
locals {
  image_url = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name2}/${var.image_name2}:latest"
}

resource "null_resource" "build_push_image" {
  triggers = { always_run = timestamp() }

  provisioner "local-exec" {
    working_dir = path.module
    command     = "docker build --platform=linux/amd64 -t ${local.image_url} . && docker push ${local.image_url}"
  }

  depends_on = [null_resource.docker_auth]
}



resource "google_cloud_run_v2_service" "chatbot" {
  name     = var.cloud_run_service_name2
  location = var.region
  project  = var.project_id
  deletion_protection = false

  template {
      containers {
        image = "europe-west1-docker.pkg.dev/${var.project_id}/${var.repository_name2}/${var.image_name2}:latest"

      env {
        name  = "CUSTOMER_API_URL"
        value = ""
      }

      env {
        name  = "OPENAI_API_KEY"
        value = var.google_api_key
      }

      env {
        name  = "WEATHERAPI_API_KEY"
        value = var.api_weather_key
      }

      ports {
        container_port = 8020
      }
      }
    }
  
  traffic {
    type = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [ null_resource.build_push_image ]
}


# Permitir acceso público
resource "google_cloud_run_service_iam_member" "invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloud_run_v2_service.chatbot.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}