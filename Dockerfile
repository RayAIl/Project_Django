FROM python:3.12

WORKDIR /Project_Django

RUN apt-get update && \
    apt-get install -y gcc wget && \
    wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz && \
    tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.6.1.tar.gz && \
    rm dockerize-linux-amd64-v0.6.1.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/app/static/upload

EXPOSE 8080

# Ждем PostgreSQL и запускаем приложение
CMD ["dockerize", "-wait", "tcp://postgres:5432", "-timeout", "30s", "uwsgi", "app.ini"]
