# Usa una imagen base de Python.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia el archivo de requisitos e instala las dependencias.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el resto del código de la aplicación.
COPY . .

# Define el comando para ejecutar el script cuando el contenedor se inicie.
CMD ["python", "main.py"]