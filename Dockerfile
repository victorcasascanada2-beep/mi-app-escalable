# Imagen base de Python ligera
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código de la app
COPY . .

# Exponemos el puerto que usa Cloud Run
EXPOSE 8080

# Comando para arrancar Streamlit en el puerto correcto
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
