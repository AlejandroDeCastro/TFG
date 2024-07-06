# Usa la imagen oficial de Python como imagen base
FROM python:3.9-slim

# Establece variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo en el contenedor
WORKDIR /CODE

# Actualiza los repositorios e instala las dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y build-essential python3-dev libmariadb-dev pkg-config

# Copia el archivo de requerimientos
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia los archivos de la aplicación al contenedor
COPY . .

# Instala el cliente MySQL para poder importar el dump
RUN apt-get update && apt-get install -y default-mysql-client

# Expone el puerto en el que la aplicación Flask va a correr
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0"]

