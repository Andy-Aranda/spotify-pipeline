# Imagen base con Python
FROM python:3.11-slim

# Setea el directorio de trabajo
WORKDIR /usr/app

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && apt-get clean

# Instala dbt + adaptador para Spark
RUN pip install --upgrade pip
RUN pip install dbt-spark

# Copia tu proyecto local al contenedor (opcional si montas con volumen)
COPY . /usr/app

# Setea variable de entorno para dbt
ENV DBT_PROFILES_DIR=/usr/app

# Comando por defecto al iniciar
CMD ["tail", "-f", "/dev/null"]