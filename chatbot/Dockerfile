# Usa una imagen base de Python 3.11 en su versión "slim"
FROM python:3.11-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos (requirements.txt) al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de la aplicación al directorio de trabajo
COPY . .

# Ejecuta el script principal del bot
CMD ["python", "telegram.py"]