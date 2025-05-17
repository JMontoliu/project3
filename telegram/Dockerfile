# telegram_gateway/Dockerfile

# Usar una imagen base de Python
FROM python:3.13-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /usr/src/app

# Copiar el archivo de requisitos primero para aprovechar el cache de Docker
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
# (Solo copiaremos la carpeta 'app' y el archivo .env si estuviera aquí)
COPY ./app ./
# Si .env estuviera en telegram_gateway/, lo copiarías así:
# COPY .env .

# Comando para ejecutar la aplicación cuando el contenedor inicie
# Asegúrate de que el .env se carga correctamente desde la ubicación correcta
# o que las variables de entorno se pasan a través de docker-compose.
CMD ["python", "main.py"]