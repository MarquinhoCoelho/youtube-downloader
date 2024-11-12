FROM python:3.10-slim

# Instala o ffmpeg e tkinter
RUN apt-get update && \
    apt-get install -y ffmpeg python3-tk && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar a aplicação Flask (ou main.py)
CMD ["python", "main.py"]
