# Dockerfile for Security Proxy (Governor)
FROM python:3.11-slim

WORKDIR /proxy-app

# Install dependencies required for cryptography on slim images
RUN apt-get update && apt-get install -y gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python packages directly for the proxy microservice
RUN pip install --no-cache-dir fastapi uvicorn cryptography PyJWT pydantic

# Copy the proxy script
COPY proxy.py .

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Run Uvicorn server
CMD ["uvicorn", "proxy:app", "--host", "0.0.0.0", "--port", "8000"]