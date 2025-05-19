# chatbot_core/Dockerfile
FROM python:3.13-slim

WORKDIR /usr/src/app

# Prevenir que Python escriba archivos .pyc al disco (opcional)
ENV PYTHONDONTWRITEBYTECODE 1
# Asegura que la salida de Python se muestre inmediatamente (útil para logs en Docker)
ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
# Asumiendo que tu código está en una subcarpeta 'app'
COPY ./app ./app

# Exponer el puerto en el que FastAPI/Uvicorn escuchará
EXPOSE 8020

# Comando para ejecutar la aplicación FastAPI con Uvicorn
# Escucha en todas las interfaces (0.0.0.0) en el puerto 8020
# --reload es para desarrollo, permite que uvicorn se reinicie si cambias el código.
# Quítalo para producción.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020", "--reload"]