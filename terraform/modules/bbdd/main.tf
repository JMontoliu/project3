resource "google_sql_database_instance" "instance" {
  name             = var.name_instance_bbdd
  region           = var.region
  database_version = var.db_version
  settings {
    tier = var.db_tier
  }

  deletion_protection  = false
}

resource "google_sql_database" "database" {
  name     = var.db_name
  instance = google_sql_database_instance.instance.name
}

resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.instance.name
  password = var.db_password
}

# DE AQUÍ HACIA ABAJO ES UNA PRUEBA DE CREACIÓN DE SCHEMA Y TABLAS
#SE TIENE QUE MODIFICAR
# Crear un schema usando un archivo SQL externo
resource "null_resource" "create_schema" {
  depends_on = [google_sql_database.database, google_sql_user.user]

  provisioner "local-exec" {
    command = <<EOT
      # Esperar a que la base de datos esté lista
      echo "Esperando 10 segundos para asegurar que la base de datos esté lista..."
      sleep 10
      
      # Procesar el archivo schema.sql para reemplazar las variables
      echo "Procesando archivo schema.sql..."
      sed 's/\${db_schema}/${var.db_schema}/g' ${path.module}/schema.sql > /tmp/schema_processed.sql
      
      # Conectar y ejecutar el script SQL
      echo "Creando schema ${var.db_schema}..."
      gcloud sql connect ${google_sql_database_instance.instance.name} \
        --user=${var.db_user} \
        --database=${var.db_name} \
        --quiet \
        < /tmp/schema_processed.sql
      
      # Limpiar
      rm /tmp/schema_processed.sql
      
      # Verificar resultado
      if [ $? -eq 0 ]; then
        echo "Schema ${var.db_schema} creado o verificado correctamente"
      else
        echo "ERROR: No se pudo crear el schema. Verifique los permisos y la conectividad."
        exit 1
      fi
    EOT
  }

  triggers = {
    instance_name = google_sql_database_instance.instance.name
    db_name = google_sql_database.database.name
    db_schema = var.db_schema
    # Si el archivo SQL cambia, esto se vuelve a ejecutar
    sql_hash = filesha256("${path.module}/schema.sql")
    # Para desarrollo
    run_every_time = timestamp()
  }
}

# Crear tablas usando un archivo SQL externo
resource "null_resource" "create_tables" {
  depends_on = [null_resource.create_schema]

  provisioner "local-exec" {
    command = <<EOT
      # Procesar el archivo tables.sql para reemplazar las variables
      echo "Procesando archivo tables.sql..."
      sed 's/\${db_schema}/${var.db_schema}/g' ${path.module}/tables.sql > /tmp/tables_processed.sql
      
      # Conectar y ejecutar el script SQL
      echo "Creando tablas en el schema ${var.db_schema}..."
      gcloud sql connect ${google_sql_database_instance.instance.name} \
        --user=${var.db_user} \
        --database=${var.db_name} \
        --quiet \
        < /tmp/tables_processed.sql
      
      # Limpiar
      rm /tmp/tables_processed.sql
      
      echo "Tablas creadas correctamente"
    EOT
  }

  triggers = {
    # Dependencia del schema
    schema_id = null_resource.create_schema.id
    # Si el archivo SQL cambia, esto se vuelve a ejecutar
    sql_hash = filesha256("${path.module}/tables.sql")
    # Para desarrollo
    run_every_time = timestamp()
  }
}