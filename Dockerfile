FROM python:3.12-slim-bullseye

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Устанавливаем зависимости ОС и dockerize
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc wget libpq-dev && \
    wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz && \
    tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.6.1.tar.gz && \
    rm dockerize-linux-amd64-v0.6.1.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем зависимости отдельно для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем директории для статики
RUN mkdir -p /app/app/static/upload && \
    python manage.py collectstatic --noinput

# Оптимизация для Django
#RUN python manage.py collectstatic --noinput  # Сбор статики

EXPOSE 8080

# Ждем PostgreSQL и запускаем приложение
CMD ["dockerize", "-wait", "tcp://postgres:5432", "-timeout", "30s", "uwsgi", "app.ini"]
