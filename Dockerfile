# 1. Imagen base oficial de Python
FROM python:3.9-slim

# 2. Configuración del directorio de trabajo
WORKDIR /app

# 3. Instalación de dependencias del sistema para que NLTK no falle
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiar archivos de dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Descargar recursos de NLTK (los que OneDrive bajaba antes)
RUN python -m textblob.download_corpora

# 6. Copiar el resto del código y la DB
COPY . .

# 7. Exponer el puerto que usa Streamlit
EXPOSE 8501

# 8. Comando para arrancar la web
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]