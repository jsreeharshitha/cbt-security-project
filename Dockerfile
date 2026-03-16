# Tier 1 & 2: Interaction + Security Proxy Logic
# Base: python:3.11-alpine for minimum resource footprint
FROM python:3.11-alpine

# Set working directory inside the container
WORKDIR /cbt-security-project

# Install system dependencies required for cryptography and scikit-learn
# These are necessary because Alpine uses musl instead of glibc
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    g++ \
    make

# TODO add Ollama here. 

# Copy only the requirements file first to leverage Docker cache
COPY requirement.txt .

# Install Python libraries
# Includes: langchain, PyJWT, scikit-learn, fastapi, uvicorn
RUN pip install --no-cache-dir -r requirement.txt

# Copy the entire project folder into the container
COPY . .

# Expose the port your Security Proxy/Middleware will run on
EXPOSE 8000

# Entry Point: Launching the main application
# This script should orchestrate the 3-tier flow
CMD ["python", "frontend/main.py"]