# Отдельный сборочный образ
FROM python:3.9-slim-bullseye as compile-image
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y gcc && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Итоговый образ, в котором будет работать бот
FROM python:3.9-slim-bullseye
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY . /app/bot
CMD ["python", "-m", "bot"]