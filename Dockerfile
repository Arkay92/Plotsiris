# Plotsiris - Global OSINT & Reconnaissance Dashboard Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package specifications
COPY pyproject.toml README.md requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY plotsiris/ ./plotsiris/
COPY assets/ ./assets/
COPY app.py main.py ./

EXPOSE 8050

ENV PLOTSIRIS_HOST="0.0.0.0"
ENV PLOTSIRIS_PORT=8050
ENV PLOTSIRIS_DEBUG=false

CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server", "--workers", "2", "--timeout", "120"]
