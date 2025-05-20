# Base de Python moderna y liviana
FROM python:3.13-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copiar archivo de requisitos e instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY ./app ./app

# Puerto por defecto de Streamlit
EXPOSE 8501

# Ejecutar Streamlit apuntando a main.py
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
