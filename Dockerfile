# Docker for Frontend Agent
# Base
FROM python:3.11-alpine
WORKDIR /cbt-security-project

# For installing system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    g++ \
    make

# TODO add Ollama here. 
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"
ENV APP_ENV="prod"

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt
COPY . .
CMD ["python", "frontend/main.py"]