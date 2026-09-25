FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 est l'interface du conteneur : c'est docker-compose.yml qui limite
# la publication du port à la machine hôte (127.0.0.1).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
