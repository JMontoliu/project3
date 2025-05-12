resource "google_artifact_registry_repository" "repo" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_name
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
  image_url = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest"
}

resource "null_resource" "build_push_image" {
  triggers = { always_run = timestamp() }

  provisioner "local-exec" {
    working_dir = path.module
    command     = "docker build --platform=linux/amd64 -t ${local.image_url} . && docker push ${local.image_url}"
  }

  depends_on = [null_resource.docker_auth]
}



resource "google_cloud_run_service" "service" {
  name     = var.cloud_run_service_name
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "europe-west1-docker.pkg.dev/${var.project_id}/${var.repository_name}/${var.image_name}:latest"

      env {
        name  = "DB_HOST"
        value = var.db_host
      }

      env {
        name  = "DB_PORT"
        value = var.port
      }

      env {
        name  = "DB_NAME"
        value = var.db_name
      }

      env {
        name  = "DB_USER"
        value = var.db_user
      }

      env {
        name  = "DB_PASSWORD"
        value = var.db_password
      }

      ports {
        container_port = 8080
      }
      }
    }
  }

  traffic {
    percent = 100
    latest_revision = true
  }

  depends_on = [ null_resource.build_push_image ]
}


# Permitir acceso público
resource "google_cloud_run_service_iam_member" "invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloud_run_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
